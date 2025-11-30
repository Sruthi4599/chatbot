import sqlite3
import bcrypt

# -----------------------------
# Initialize DB and tables
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Scores table
    c.execute("""
    CREATE TABLE IF NOT EXISTS scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        total INTEGER,
        date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Check if 'topic' column exists, if not, add it
    c.execute("PRAGMA table_info(scores)")
    columns = [col[1] for col in c.fetchall()]
    if "topic" not in columns:
        c.execute("ALTER TABLE scores ADD COLUMN topic TEXT")
        print("Added 'topic' column to scores table.")

    conn.commit()
    conn.close()

# -----------------------------
# Register user
# -----------------------------
def register_user(username, password):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# -----------------------------
# Authenticate user
# -----------------------------
def authenticate_user(username, password):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT password, id FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return result[1]  # Return user_id
    return None

# -----------------------------
# Save score
# -----------------------------
def save_score(user_id, topic, score, total, date):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO scores (user_id, topic, score, total, date) VALUES (?, ?, ?, ?, ?)",
        (user_id, topic, score, total, date)
    )
    conn.commit()
    conn.close()

# -----------------------------
# Get scores
# -----------------------------
def get_scores(user_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT topic, score, total, date FROM scores WHERE user_id=? ORDER BY date", (user_id,))
    results = c.fetchall()
    conn.close()
    return results
