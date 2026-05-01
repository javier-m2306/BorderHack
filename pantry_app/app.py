from flask import Flask, render_template, request, session, redirect, url_for
import uuid
# Re-importing the function that was causing the "UndefinedVariable" error
from database import generate_qrcode 

app = Flask(__name__)
app.secret_key = 'utep_borderhack_2026' # Essential for session management

# 1. State: Selecting Pantry (Map View)
@app.route('/')
def index():
    return render_template('index.html')

# 2. State: Build List (Inventory Selection)
@app.route('/build', methods=['GET', 'POST'])
def build_list():
    if request.method == 'POST':
        selected_items = request.form.getlist('items')
        session['current_order'] = selected_items
        return redirect(url_for('checkout'))
    
    # Static inventory for demo; real data comes from pantry_food table
    food_inventory = ["Rice", "Beans", "Pasta", "Canned Corn", "Peanut Butter"]
    return render_template('build_list.html', food=food_inventory)

# 3. State: Secure Confirmation
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        selected_items = request.form.getlist('items')
        session['current_order'] = selected_items
    return render_template('checkout.html')

# 4. State: Awaiting Pickup (QR Generation)
@app.route('/confirm', methods=['POST'])
def confirm():
    # 1. Create the ID
    qr_id = str(uuid.uuid4())[:8].upper()
    
    # 2. CALL THE GENERATOR (This was missing in your last paste)
    generate_qrcode(qr_id)
    
    # 3. Pass pickup_id so the HTML can see it
    return render_template('pickup.html', pickup_id=qr_id)

if __name__ == '__main__':
    # Running on port 5001 for the BorderHack demo
    app.run(debug=True, port=5001)