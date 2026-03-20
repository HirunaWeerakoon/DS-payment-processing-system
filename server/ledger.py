import sqlite3, json, os

# Define database path for persistence [cite: 249]
DB_PATH = os.environ.get('DB_PATH', 'payments.db')

def conn():
    """Establish connection to SQLite [cite: 251]"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create the payments table if it does not exist [cite: 253]"""
    with conn() as c:
        c.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp REAL NOT NULL,
                status TEXT NOT NULL,
                server TEXT
            )
        ''') # [cite: 257-267]

def record_payment(payment):
    """Insert a payment. Silently ignores duplicates (idempotent) [cite: 268-269]"""
    with conn() as c:
        c.execute('''
            INSERT OR IGNORE INTO payments 
            (id, sender, receiver, amount, timestamp, status, server)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment["id"], payment["sender"], payment["receiver"],
            payment["amount"], payment["timestamp"],
            payment["status"], payment.get("server")
        )) # [cite: 271-277]

def get_all_payments():
    """Return all payments ordered by timestamp [cite: 280-281]"""
    with conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute('SELECT * FROM payments ORDER BY timestamp DESC').fetchall()
        return [dict(r) for r in rows] # [cite: 286-288]

def payment_exists(payment_id):
    """Check for duplicate before inserting [cite: 289-290]"""
    with conn() as c:
        r = c.execute('SELECT 1 FROM payments WHERE id=?', (payment_id,)).fetchone()
        return r is not None # [cite: 292]