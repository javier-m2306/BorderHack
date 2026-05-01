from flask import Flask, render_template, request, session, redirect, url_for
import uuid
from database import generate_qrcode, init_db, make_new_account, get_connection

app = Flask(__name__)
app.secret_key = 'utep_borderhack_2026'


# ── DB helpers added here to keep database.py minimal ──────────────

def get_account_by_number(number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM account WHERE number = ?", (number,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_qr_for_account(account_id, qr_code):
    """Save (or replace) the single active QR for this account."""
    conn = get_connection()
    cursor = conn.cursor()
    # Store on the account row itself — add column if it doesn't exist yet
    try:
        cursor.execute("ALTER TABLE account ADD COLUMN active_qr TEXT")
        conn.commit()
    except Exception:
        pass  # column already exists
    cursor.execute(
        "UPDATE account SET active_qr = ? WHERE id = ?",
        (qr_code, account_id)
    )
    conn.commit()
    conn.close()

def get_qr_for_account(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT active_qr FROM account WHERE id = ?", (account_id,))
        row = cursor.fetchone()
        conn.close()
        return row["active_qr"] if row else None
    except Exception:
        conn.close()
        return None


# ── Routes ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ── Auth ────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        number = request.form.get('number', '').strip().upper()
        account = get_account_by_number(number)
        if account:
            session['account_id'] = account['id']
            session['account_name'] = account['name']
            session['account_number'] = account['number']
            return redirect(url_for('index'))
        else:
            error = "Student ID not found. Please register first."
    return render_template('login.html', error=error)


@app.route('/register', methods=['POST'])
def register():
    number = request.form.get('number', '').strip().upper()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()

    if not (number and name and email):
        return render_template('login.html', error="All fields are required.")

    existing = get_account_by_number(number)
    if existing:
        return render_template('login.html', error="That ID is already registered. Please log in.")

    try:
        account_id = make_new_account(number, email, name)
        session['account_id'] = account_id
        session['account_name'] = name
        session['account_number'] = number
        return redirect(url_for('index'))
    except Exception as e:
        return render_template('login.html', error=f"Registration failed: {e}")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ── Order flow ──────────────────────────────────────────────────────

@app.route('/build', methods=['GET', 'POST'])
def build_list():
    if request.method == 'POST':
        selected_items = request.form.getlist('items')
        session['current_order'] = selected_items
        return redirect(url_for('checkout'))

    food_inventory = ["Rice", "Beans", "Pasta", "Canned Corn", "Peanut Butter"]
    return render_template('build_list.html', food=food_inventory)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        selected_items = request.form.getlist('items')
        session['current_order'] = selected_items
    return render_template('checkout.html')


@app.route('/confirm', methods=['POST'])
def confirm():
    # If logged in, check for an existing QR — one at a time rule
    account_id = session.get('account_id')
    existing_qr = get_qr_for_account(account_id) if account_id else None

    if existing_qr:
        # Already have an active QR — show it instead of making a new one
        return render_template('pickup.html', pickup_id=existing_qr, reused=True)

    # Generate a new QR
    qr_id = str(uuid.uuid4())[:8].upper()
    generate_qrcode(qr_id)

    # Persist it if the user is logged in
    if account_id:
        save_qr_for_account(account_id, qr_id)

    return render_template('pickup.html', pickup_id=qr_id, reused=False)


@app.route('/my-qr')
def my_qr():
    """Let a logged-in user retrieve their active QR after navigating away."""
    account_id = session.get('account_id')
    if not account_id:
        return redirect(url_for('login'))

    existing_qr = get_qr_for_account(account_id)
    if existing_qr:
        return render_template('pickup.html', pickup_id=existing_qr, reused=True)

    return redirect(url_for('build_list'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)