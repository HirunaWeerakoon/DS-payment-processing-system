# server/payment_object.py
import uuid
import time

def new_payment(sender, receiver, amount):
    return {
        "id":        str(uuid.uuid4()),
        "sender":    sender,
        "receiver":  receiver,
        "amount":    float(amount),
        "timestamp": time.time(),   # Member 3 will replace this with now()
        "status":    "pending",
        "server":    None
    }