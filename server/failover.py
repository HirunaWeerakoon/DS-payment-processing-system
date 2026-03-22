import requests
from fault_monitor import get_live_servers

def send_payment_with_failover(payment_data):
    """Try each live server in turn until one succeeds."""
    live = get_live_servers()
    if not live:
        return {"status": "failed", "reason": "all servers down"}

    for srv in live:
        try:
            r = requests.post(
                srv["url"] + "/pay",
                json=payment_data,
                timeout=3
            )
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"[Failover] {srv['id']} failed: {e}, trying next...")
            continue

    return {"status": "failed", "reason": "all retries exhausted"}

def recover_node(server_id):
    """Called when a downed node comes back online."""
    from fault_monitor import SERVERS
    for srv in SERVERS:
        if srv["id"] == server_id:
            srv["status"] = "UP"
            srv["misses"] = 0
            print(f"[Failover] Server {server_id} recovered.")
            return True
    return False