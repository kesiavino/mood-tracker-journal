# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app) 

DATABASE = 'mood_journal.db'

def init_db():
    """Initializes the database schema if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            mood TEXT NOT NULL,
            entry_text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

@app.route('/')
def index():
    """Serves the main HTML file."""
    return render_template('index.html')


@app.route('/api/entries', methods=['GET', 'POST'])
def handle_entries():
    """
    Handles fetching and adding journal entries.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT id, date, mood, entry_text FROM journal_entries ORDER BY date DESC")
        entries = []
        for row in cursor.fetchall():
            entries.append({
                'id': row[0],
                'date': row[1],
                'mood': row[2],
                'entry_text': row[3]
            })
        conn.close()
        return jsonify(entries)

    elif request.method == 'POST':
        data = request.get_json()
        date = data.get('date')
        mood = data.get('mood')
        entry_text = data.get('entry_text')

        if not all([date, mood, entry_text]):
            conn.close()
            return jsonify({'error': 'Missing data'}), 400

        # Basic validation for date format (YYYY-MM-DD)
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            conn.close()
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        cursor.execute(
            "INSERT INTO journal_entries (date, mood, entry_text) VALUES (?, ?, ?)",
            (date, mood, entry_text)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Entry added successfully', 'id': cursor.lastrowid}), 201

if __name__ == '__main__':
    init_db()  
    app.run(debug=True) 