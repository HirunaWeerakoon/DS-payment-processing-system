import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
import sqlite3, uuid, time, pytest
os.environ['DB_PATH'] = ':memory:' 

import ledger
from ledger import init_db, record_payment, get_all_payments, payment_exists

@pytest.fixture(autouse=True)
def fresh_db(monkeypatch):
    """Give every test a brand-new in-memory database."""
    conn = sqlite3.connect(':memory:')
    monkeypatch.setattr(ledger, 'conn', lambda: conn)
    init_db()
    yield
    conn.close()