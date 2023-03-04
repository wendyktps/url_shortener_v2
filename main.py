import sqlite3
import pyshorteners
from flask import Flask, render_template, redirect, request

app = Flask(__name__, template_folder='../templates')
con = sqlite3.connect("urls.db", check_same_thread=False)
cur = con.cursor()
shortener = pyshorteners.Shortener()

cur.execute('''CREATE TABLE if not exists url (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullURL TEXT NOT NULL,
    shortenURL TEXT,
    times INTEGER DEFAULT 0 NOT NULL)''')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return show_the_page()
    if request.method == 'POST':
        return shorten_link()


def show_the_page():
    return render_template('index.html')


def shorten_link():
    full_url = request.form['url']
    res = cur.execute(f"SELECT fullURL FROM url WHERE fullURL = '{full_url}'")

    if res.fetchone() is None:
        cur.execute(
            f"INSERT INTO url (fullURL, times) VALUES ('{full_url}', 0)")
        id = cur.execute(
            f"SELECT id FROM url WHERE fullURL = '{full_url}'").fetchone()
        cur.execute(
            f"UPDATE url SET shortenURL = '{f'http://127.0.0.1:5000/{id[0]}'}' WHERE fullURL = '{full_url}'")

    short_url = cur.execute(
        f"SELECT shortenURL FROM url WHERE fullURL = '{full_url}'").fetchone()[0]

    cur.execute(
        f"UPDATE url SET times = times + 1 WHERE fullURL = '{full_url}'")

    times = cur.execute(
        f"SELECT times FROM url WHERE fullURL = '{full_url}'").fetchone()[0]

    con.commit()

    return render_template('index.html', full_url=full_url, url=short_url, times=times)


@app.route('/<id>', methods=['GET'])
def full_url_redirect(id):
    full_url = cur.execute(
        f"SELECT fullURL FROM url WHERE id={id}").fetchone()[0]
    if 'https://' not in full_url:
        full_url = f'https://{full_url}'
    return redirect(full_url)


if __name__ == '__main__':
    app.run(debug=True)
