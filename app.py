from flask import Flask, request, redirect, render_template, url_for, jsonify
import string, random
import sqlite3

app = Flask(__name__)
DB_FILE = 'shortener.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            long_url TEXT
        )''')
        conn.commit()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def insert_url(short_code, long_url):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
        conn.commit()

def get_long_url(short_code):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
        result = c.fetchone()
        return result[0] if result else None

@app.route('/shorten', methods=['POST'])
def shorten():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        long_url = data['url']
        short_code = generate_short_code()
        insert_url(short_code, long_url)
        short_url = request.host_url + short_code
        return jsonify({'shortUrl': short_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/<short_code>')
def redirect_short_url(short_code):
    long_url = get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    return "URL not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=3000, host='0.0.0.0')
