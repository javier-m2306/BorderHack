Grab and GO! 🍎
🚀 View Live Demo 

https://borderhack-production.up.railway.app/

Grab and GO! is a "Dignity-First" student pantry management system. By replacing traditional physical ID checks with secure, anonymized QR tokens, we eliminate the "Humiliation and Fear" that prevents 95% of food-insecure students from seeking help.

Core Technology Stack
Backend: Python (Flask) — Manages the state transitions and session logic.

Database: SQLite — Handles relational mapping between students and inventory.

Frontend: Tailwind CSS — Provides a modern, responsive, and accessible UI.

Infrastructure: Deployed via Railway for high-availability access.

Google Technology Integration
We utilized Google Gemini as a core development collaborator to:

Research & Strategy: Analyze statistics on student food scarcity and psychological barriers.

System Architecture: Design complex relational schemas for anonymized fulfillment.

Real-Time Troubleshooting: Resolve critical database integrity and deployment errors during the 24-hour sprint.

Features
Anonymized Selection: Students choose what they need without exposing their identity.

Secure Tokenization: Unique UUID-based QR codes generated for every pickup.

Mobile-First Design: Easy access for students on the move at the Student Union.

Quick Start Guide (Local Setup)
To run this project locally, follow these steps:

1. Prerequisites
Python 3.x

Pip

2. Installation
Bash
git clone https://github.com/javier-m2306/BorderHack.git
cd BorderHack
pip install -r requirements.txt
3. Initialization & Execution
Bash
# Step 1: Initialize the relational database
python database.py

# Step 2: Launch the Flask server
python app.py
Access the application at: [http://127.0.0.1:5001](http://127.0.0.1:5001)

Future Vision
While this MVP focuses on the student pantry, our goal is to scale Grab and GO! into a universal campus resource platform—supporting textbook lending, hygiene supplies, and emergency tech equipment, all while maintaining student dignity as our top priority.
