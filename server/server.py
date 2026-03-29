# server/server.py
import os
import sys
import time
from flask import Flask, request, jsonify

# sys.path MUST come before any local imports
sys.path.insert(0, os.path.dirname(__file__))

# Local module imports — all in correct order now
from consensus import PaymentNode
from ledger import init_db
from payment_object import new_payment
from time_sync import sync_clock, now          # M3
from fault_monitor import start as start_monitor, get_status  # M1
from replication import replicate_to_peers     # M2
from log_ordering import add_to_buffer         # M3

app = Flask(__name__)

SERVER_ID  = os.environ.get('SERVER_ID',  'A')
SELF_PORT  = int(os.environ.get('SELF_PORT',  '5001'))
RAFT_PORT  = int(os.environ.get('RAFT_PORT',  '4001'))
RAFT_PEERS = os.environ.get('RAFT_PEERS', '')

peer_list = [p.strip() for p in RAFT_PEERS.split(',') if p.strip()]
self_addr  = f'127.0.0.1:{RAFT_PORT}'

node = PaymentNode(self_addr, peer_list)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'server': SERVER_ID}), 200

@app.route('/status')               # NEW — needed by UI dashboard
def status():
    return jsonify(get_status()), 200

@app.route('/pay', methods=['POST'])
def pay():
    data = request.get_json()
    payment = new_payment(
        sender   = data['sender'],
        receiver = data['receiver'],
        amount   = data['amount']
    )
    payment['timestamp'] = now()    # M3 NTP time
    payment['server']    = SERVER_ID
    payment['status']    = 'success'

    node.add_payment(payment)       # Raft consensus replication
    replicate_to_peers(payment)     # M2 backup broadcast

    return jsonify(payment), 200

@app.route('/payments')
def payments():
    return jsonify(node.get_payments()), 200

@app.route('/replicate', methods=['POST'])
def replicate():
    from ledger import record_payment, payment_exists
    data = request.get_json()
    add_to_buffer(data)             # M3 log ordering — correct timestamp
    if not payment_exists(data['id']):
        record_payment(data)
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    init_db()
    sync_clock()                    # M3 NTP sync on startup
    start_monitor()                 # M1 heartbeat thread starts
    print(f'[Server {SERVER_ID}] Starting on port {SELF_PORT}, Raft on {RAFT_PORT}')
    print(f'[Server {SERVER_ID}] Peers: {peer_list}')
    app.run(port=SELF_PORT, debug=False)