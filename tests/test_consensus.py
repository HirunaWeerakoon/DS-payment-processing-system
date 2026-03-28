# tests/test_consensus.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

import requests
import time

BASE_A = "http://127.0.0.1:5001"
BASE_B = "http://127.0.0.1:5002"
BASE_C = "http://127.0.0.1:5003"

def make_payment(sender, receiver, amount, port=5001):
    r = requests.post(
        f"http://127.0.0.1:{port}/pay",
        json={"sender": sender, "receiver": receiver, "amount": amount},
        timeout=5
    )
    return r.json()

def test_payment_returns_success():
    """A payment sent to Server A returns status success."""
    result = make_payment("alice", "bob", 10.00)
    assert result["status"] == "success"
    assert result["sender"] == "alice"
    assert result["receiver"] == "bob"
    assert result["amount"] == 10.00

def test_payment_has_valid_id():
    """Every payment gets a unique UUID."""
    r1 = make_payment("alice", "bob", 5.00)
    r2 = make_payment("carol", "dave", 8.00)
    assert r1["id"] != r2["id"]
    assert len(r1["id"]) == 36   # UUID format

def test_payment_has_timestamp():
    """Payment timestamp is a recent Unix epoch float."""
    result = make_payment("alice", "bob", 1.00)
    assert isinstance(result["timestamp"], float)
    assert abs(result["timestamp"] - time.time()) < 10

def test_raft_replication_to_all_nodes():
    """A payment sent to Server A appears on B and C — Raft working."""
    result = make_payment("alice", "bob", 99.00)
    payment_id = result["id"]
    time.sleep(1)   # give Raft time to replicate

    for base in [BASE_A, BASE_B, BASE_C]:
        payments = requests.get(f"{base}/payments").json()
        ids = [p["id"] for p in payments]
        assert payment_id in ids, f"Payment missing on {base}"

def test_payment_to_different_servers_all_replicate():
    """Payments sent to different servers all end up on every node."""
    r1 = make_payment("alice", "bob",   20.00, port=5001)
    r2 = make_payment("carol", "dave",  30.00, port=5002)
    r3 = make_payment("eve",   "frank", 40.00, port=5003)
    time.sleep(1)

    all_ids = {r1["id"], r2["id"], r3["id"]}

    for base in [BASE_A, BASE_B, BASE_C]:
        payments = requests.get(f"{base}/payments").json()
        ids = set(p["id"] for p in payments)
        for pid in all_ids:
            assert pid in ids, f"Payment {pid} missing on {base}"

def test_health_endpoint_all_nodes():
    """All 3 nodes respond to /health."""
    for base, sid in [(BASE_A,"A"), (BASE_B,"B"), (BASE_C,"C")]:
        r = requests.get(f"{base}/health").json()
        assert r["status"] == "ok"
        assert r["server"] == sid

def test_status_shows_all_up():
    """Fault monitor reports all 3 nodes as UP."""
    r = requests.get(f"{BASE_A}/status").json()
    assert r["A"] == "UP"
    assert r["B"] == "UP"
    assert r["C"] == "UP"