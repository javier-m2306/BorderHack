import sqlite3
import qrcode 
import os

DB_NAME = "pantry_app.db"



def generate_qrcode(qr_value):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)
    img = qrcode.make(qr_value)
    img.save(os.path.join(static_dir, f"{qr_value}.png"))


DB_NAME = "pantry_app.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # --- Account ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS account (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            number      TEXT    NOT NULL UNIQUE,
            email       TEXT    NOT NULL UNIQUE,
            name        TEXT    NOT NULL
        )
    """)

    # --- Grocery list (one per account) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grocery_list (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE
        )
    """)

    # --- Items inside a grocery list ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grocery_list_item (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            grocery_list_id INTEGER NOT NULL,
            food_name       TEXT    NOT NULL,
            FOREIGN KEY (grocery_list_id) REFERENCES grocery_list(id) ON DELETE CASCADE
        )
    """)

    # --- Pantry ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pantry (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            location    TEXT    NOT NULL
        )
    """)

    # --- Food available at a pantry ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pantry_food (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pantry_id   INTEGER NOT NULL,
            food_name   TEXT    NOT NULL,
            FOREIGN KEY (pantry_id) REFERENCES pantry(id) ON DELETE CASCADE
        )
    """)

    # --- Bag (created by pantry, linked to an account's order) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bag (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pantry_id   INTEGER NOT NULL,
            account_id  INTEGER NOT NULL,
            qr_code     TEXT    UNIQUE,
            FOREIGN KEY (pantry_id)  REFERENCES pantry(id)  ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE
        )
    """)

    # --- Items packed into a bag (copied from grocery list at order time) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bag_item (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            bag_id      INTEGER NOT NULL,
            food_name   TEXT    NOT NULL,
            FOREIGN KEY (bag_id) REFERENCES bag(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialised: pantry_app.db")


# ── Helper functions ────────────────────────────────────────────────

def make_new_account(number, email, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO account (number, email, name) VALUES (?, ?, ?)",
        (number, email, name)
    )
    account_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO grocery_list (account_id) VALUES (?)",
        (account_id,)
    )
    conn.commit()
    conn.close()
    return account_id

def add_food_to_list(account_id, food_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM grocery_list WHERE account_id = ?", (account_id,)
    )
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "INSERT INTO grocery_list_item (grocery_list_id, food_name) VALUES (?, ?)",
            (row["id"], food_name)
        )
    conn.commit()
    conn.close()

def remove_food_from_list(account_id, food_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM grocery_list WHERE account_id = ?", (account_id,)
    )
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "DELETE FROM grocery_list_item WHERE grocery_list_id = ? AND food_name = ?",
            (row["id"], food_name)
        )
    conn.commit()
    conn.close()

def get_grocery_list(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gli.food_name
        FROM grocery_list gl
        JOIN grocery_list_item gli ON gli.grocery_list_id = gl.id
        WHERE gl.account_id = ?
    """, (account_id,))
    items = [r["food_name"] for r in cursor.fetchall()]
    conn.close()
    return items

def add_pantry(name, location):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pantry (name, location) VALUES (?, ?)", (name, location)
    )
    pantry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pantry_id

def add_food_to_pantry(pantry_id, food_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pantry_food (pantry_id, food_name) VALUES (?, ?)",
        (pantry_id, food_name)
    )
    conn.commit()
    conn.close()

def get_pantry_food(pantry_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT food_name FROM pantry_food WHERE pantry_id = ?", (pantry_id,)
    )
    items = [r["food_name"] for r in cursor.fetchall()]
    conn.close()
    return items

def prepare_bag(pantry_id, account_id, qr_code):
    """Create a bag from the account's current grocery list and store it."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bag (pantry_id, account_id, qr_code) VALUES (?, ?, ?)",
        (pantry_id, account_id, qr_code)
    )
    bag_id = cursor.lastrowid
    cursor.execute("""
        SELECT gli.food_name
        FROM grocery_list gl
        JOIN grocery_list_item gli ON gli.grocery_list_id = gl.id
        WHERE gl.account_id = ?
    """, (account_id,))
    for row in cursor.fetchall():
        cursor.execute(
            "INSERT INTO bag_item (bag_id, food_name) VALUES (?, ?)",
            (bag_id, row["food_name"])
        )
    conn.commit()
    conn.close()
    return bag_id

def get_bag_by_qr(qr_code):
    """Look up a bag and its contents by QR code (used at checkout)."""
    conn = get_connection()
    cursor = conn.cursor()
    print("Looking for QR:", qr_code)
    cursor.execute("""
        SELECT b.id, b.qr_code, a.name AS student_name, a.number
        FROM bag b
        JOIN account a ON a.id = b.account_id
        WHERE b.qr_code = ?
    """, (qr_code,))
    bag = cursor.fetchone()
    if bag:
        cursor.execute(
            "SELECT food_name FROM bag_item WHERE bag_id = ?", (bag["id"],)
        )
        contents = [r["food_name"] for r in cursor.fetchall()]
        result = dict(bag)
        result["contents"] = contents
        conn.close()
        return result
    conn.close()
    return None


# ── Quick smoke test ────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()

    # Create a pantry
    p_id = add_pantry("Main Campus Pantry", "Student Union Room 101")
    add_food_to_pantry(p_id, "Rice")
    add_food_to_pantry(p_id, "Canned Beans")
    add_food_to_pantry(p_id, "Pasta")
    print("Pantry food:", get_pantry_food(p_id))

    # Create an account (auto-creates grocery list)
    a_id = make_new_account("S001", "student@utep.edu", "Alex Rivera")

    

    # Student builds their grocery list
    add_food_to_list(a_id, "Rice")
    add_food_to_list(a_id, "Pasta")
    print("Grocery list:", get_grocery_list(a_id))

    # Pantry prepares the bag and generates QR
    qr_code = "QR-S001-001"
    generate_qrcode(qr_code)
    bag_id = prepare_bag(p_id, a_id, qr_code)
    bag_id = prepare_bag(p_id, a_id, qr_code="QR-S001-001")
    print("Bag created, id:", bag_id)

    # At pickup — scan QR and retrieve bag
    bag = get_bag_by_qr("QR-S001-001")
    print("Bag at pickup:", bag)