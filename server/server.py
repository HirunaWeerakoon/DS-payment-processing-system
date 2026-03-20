# Add this route to server/server.py
from ledger import record_payment, payment_exists

@app.route('/replicate', methods=['POST'])
def replicate():
    """Receives replicated data from peer nodes [cite: 320-321]"""
    data = request.get_json()
    
    # Prevents duplicate entries and infinite loops [cite: 324]
    if not payment_exists(data['id']):
        record_payment(data) # [cite: 327]
        return {'status': 'ok'}, 200
        
    return {'status': 'ignored', 'reason': 'already_exists'}, 200