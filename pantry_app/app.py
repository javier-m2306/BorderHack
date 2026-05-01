from flask import Flask, render_template, request, redirect, url_for, session
import uuid

# --- 1. THE DATABASE BRIDGE (KEEP THIS COMMENTED OUT FOR NOW) ---
# Once your teammate is done, you just remove the '#' from these lines.
# from database import (
#     init_db, make_new_account, add_food_to_list, get_grocery_list, 
#     add_pantry, add_food_to_pantry, get_pantry_food, prepare_bag
# )

app = Flask(__name__)
app.secret_key = 'ghost_pantry_secret'

# --- 2. YOUR FRONTEND ROUTES ---

@app.route('/')
def index():
    # This renders your index.html (Pantry Selection state)
    return render_template('index.html')

@app.route('/build')
def build():
    # This is "Mock Data." It lets you design build_list.html right now.
    # We're using a list of 6 items to test your 5-item limit logic.
    fake_inventory = ["Rice", "Pasta", "Canned Beans", "Peanut Butter", "Soap", "Milk"]
    return render_template('build_list.html', food=fake_inventory)

@app.route('/pickup')
def pickup():
    # This renders your pickup.html (QR code/Awaiting Pickup state)
    return render_template('pickup.html', qr="GHOST-789")

if __name__ == '__main__':
    # We aren't calling init_db() yet because the file isn't ready
    app.run(debug=True, port=5001)