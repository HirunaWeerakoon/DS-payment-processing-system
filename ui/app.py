# ui/app.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from flask import Flask, render_template, request, jsonify
from failover import send_payment_with_failover
from fault_monitor import get_status, start as start_monitor
import requests

app = Flask(__name__)

SERVERS = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003",
]

def get_any_live_server():
    """Try each server in turn and return the first one that responds."""
    for url in SERVERS:
        try:
            r = requests.get(f"{url}/health", timeout=1)
            if r.status_code == 200:
                return url
        except Exception:
            continue
    return None


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ── API routes called by the dashboard (AJAX) ─────────────────────────────────

@app.route('/api/status')
def api_status():
    """Return UP/DOWN status of all 3 payment servers."""
    return jsonify(get_status())


@app.route('/api/payments')
def api_payments():
    """Fetch all payments from any live server."""
    url = get_any_live_server()
    if not url:
        return jsonify([])
    try:
        r = requests.get(f"{url}/payments", timeout=3)
        return jsonify(r.json())
    except Exception:
        return jsonify([])


@app.route('/api/pay', methods=['POST'])
def api_pay():
    """
    Accept a payment from the UI form and forward it using failover logic.
    Tries each live server in turn — never fails silently.
    """
    data = request.get_json()

    if not data or not all(k in data for k in ['sender', 'receiver', 'amount']):
        return jsonify({'status': 'failed', 'reason': 'Missing fields'}), 400

    try:
        data['amount'] = float(data['amount'])
    except (ValueError, TypeError):
        return jsonify({'status': 'failed', 'reason': 'Invalid amount'}), 400

    result = send_payment_with_failover(data)

    if result.get('status') == 'failed':
        return jsonify(result), 503

    return jsonify(result), 200


if __name__ == '__main__':
    start_monitor()   # start heartbeat thread so /api/status works
    print("[UI] Dashboard running at http://127.0.0.1:8080")
    app.run(port=8080, debug=False)
