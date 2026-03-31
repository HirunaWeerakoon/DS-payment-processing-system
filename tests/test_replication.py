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

def make_payment(sender='alice', receiver='bob', amount=10.0):
    return {
        'id': str(uuid.uuid4()),
        'sender': sender,
        'receiver': receiver,
        'amount': float(amount),
        'timestamp': time.time(),
        'status': 'success',
        'server': 'A',
    }

def test_record_payment_stores_correctly():
    p = make_payment('alice', 'bob', 50.0)
    record_payment(p)
    all_p = get_all_payments()
    assert len(all_p) == 1
    assert all_p[0]['sender'] == 'alice'

def test_payment_exists_returns_true():
    p = make_payment()
    record_payment(p)
    assert payment_exists(p['id']) is True

def test_deduplication_insert_or_ignore():
    """Inserting the same payment twice does not create a duplicate."""
    p = make_payment()
    record_payment(p)
    record_payment(p) # This second call should be ignored by the DB
    all_p = get_all_payments()
    assert len(all_p) == 1

def test_payments_ordered_by_timestamp_desc():
    p1 = make_payment(); p1['timestamp'] = 1000.0
    p2 = make_payment(); p2['timestamp'] = 2000.0
    for p in [p1, p2]: record_payment(p)
    all_p = get_all_payments()
    assert all_p[0]['timestamp'] == 2000.0