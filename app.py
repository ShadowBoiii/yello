from flask import Flask, render_template, request, redirect, url_for, Markup, render_template_string
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Subtle SSTI vulnerability through template filter
@app.template_filter('greet')
def greet_filter(name):
    # Looks like an innocent greeting formatter
    # But actually renders the name as a template string
    greeting_template = "Dear " + str(name)
    return render_template_string(greeting_template)

def init_db():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  message TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('SELECT * FROM feedback ORDER BY timestamp DESC')
    feedbacks = c.fetchall()
    conn.close()
    return render_template('index.html', feedbacks=feedbacks)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        
        conn = sqlite3.connect('feedback.db')
        c = conn.cursor()
        c.execute('INSERT INTO feedback (name, message) VALUES (?, ?)',
                 (name, message))
        conn.commit()
        conn.close()
        return redirect(url_for('thankyou') + f'?name={name}')
    return render_template('submit.html')

@app.route('/thankyou')
def thankyou():
    name = request.args.get('name', '')
    return render_template('thankyou.html', name=name)

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 