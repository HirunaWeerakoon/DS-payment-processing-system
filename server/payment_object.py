# server/payment_object.py
import uuid
import time

def new_payment(sender, receiver, amount):
    return {
        "id":        str(uuid.uuid4()),
        "sender":    sender,
        "receiver":  receiver,
        "amount":    float(amount),
        "timestamp": 0,
        "status":    "pending",
        "server":    None
    }