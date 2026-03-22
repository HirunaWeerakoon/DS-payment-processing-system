# server/server.py
import os
import sys
import time
from flask import Flask, request, jsonify

# Make sure Python can find the other modules in /server
sys.path.insert(0, os.path.dirname(__file__))

from consensus import PaymentNode
from ledger import init_db
from payment_object import new_payment

app = Flask(__name__)

# ── Config from environment variables ─────────────────────────────────────────
SERVER_ID  = os.environ.get('SERVER_ID',  'A')
SELF_PORT  = int(os.environ.get('SELF_PORT',  '5001'))
RAFT_PORT  = int(os.environ.get('RAFT_PORT',  '4001'))
RAFT_PEERS = os.environ.get('RAFT_PEERS', '')   # comma-separated

peer_list = [p.strip() for p in RAFT_PEERS.split(',') if p.strip()]
self_addr  = f'127.0.0.1:{RAFT_PORT}'

# Start the Raft node
node = PaymentNode(self_addr, peer_list)

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/health')
def health():
    """Member 1's fault monitor pings this endpoint."""
    return jsonify({'status': 'ok', 'server': SERVER_ID}), 200

@app.route('/pay', methods=['POST'])
def pay():
    """Accept a payment, timestamp it, and replicate via Raft."""
    data = request.get_json()

    payment = new_payment(
        sender   = data['sender'],
        receiver = data['receiver'],
        amount   = data['amount']
    )
    payment['timestamp'] = time.time()   # Member 3 replaces this with now()
    payment['server']    = SERVER_ID
    payment['status']    = 'success'

    # This one call replicates the payment to ALL nodes via Raft
    node.add_payment(payment)

    return jsonify(payment), 200

@app.route('/payments')
def payments():
    """Return all payments from this node's local ledger."""
    return jsonify(node.get_payments()), 200

@app.route('/replicate', methods=['POST'])
def replicate():
    """Member 2's replication module calls this endpoint."""
    from ledger import record_payment, payment_exists
    data = request.get_json()
    if not payment_exists(data['id']):
        record_payment(data)
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    init_db()
    print(f'[Server {SERVER_ID}] Starting on port {SELF_PORT}, Raft on {RAFT_PORT}')
    print(f'[Server {SERVER_ID}] Raft peers: {peer_list}')
    app.run(port=SELF_PORT, debug=False)