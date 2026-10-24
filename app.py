# ATENȚIE: aplicație vulnerabilă INTENȚIONAT, pentru demo de securitate.
# Nu o rula expusă în internet.
import sqlite3
import subprocess

import yaml
from flask import Flask, request

app = Flask(__name__)

# Secret FALS pus intenționat, ca să-l prindă Gitleaks.
AWS_ACCESS_KEY_ID = "AKIAZ4Q7RXN2B3HKD5WP"
AWS_SECRET_ACCESS_KEY = "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"

DB_PATH = "users.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users (name, email) VALUES ('alice', 'alice@example.com')")
    conn.execute("INSERT INTO users (name, email) VALUES ('bob', 'bob@example.com')")
    conn.commit()
    conn.close()


# VULN 1: SQL injection (CWE-89). Exploit: /users?name=' OR 1=1 --
@app.route("/users")
def users():
    name = request.args.get("name", "")
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(f"SELECT id, name, email FROM users WHERE name = '{name}'").fetchall()
    conn.close()
    return {"users": rows}


# VULN 2: command injection (CWE-78). Exploit: /ping?host=127.0.0.1;id
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    out = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True)
    return {"output": out.stdout}


# VULN 3: deserializare nesigură (CWE-502) cu yaml.load fără SafeLoader
@app.route("/config", methods=["POST"])
def config():
    data = yaml.load(request.data, Loader=yaml.Loader)
    return {"parsed": str(data)}


if __name__ == "__main__":
    init_db()
    # VULN 4: debug=True (security misconfiguration)
    app.run(host="0.0.0.0", port=5000, debug=True)
