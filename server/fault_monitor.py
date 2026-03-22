import threading, time, requests

SERVERS = [
    {"id": "A", "url": "http://127.0.0.1:5001", "status": "UP", "misses": 0},
    {"id": "B", "url": "http://127.0.0.1:5002", "status": "UP", "misses": 0},
    {"id": "C", "url": "http://127.0.0.1:5003", "status": "UP", "misses": 0},
]

PING_INTERVAL = 2
MAX_MISSES = 3

def _ping(server):
    try:
        r = requests.get(server["url"] + "/health", timeout=1)
        return r.status_code == 200
    except Exception:
        return False

def _monitor_loop():
    while True:
        for srv in SERVERS:
            alive = _ping(srv)
            if alive:
                srv["misses"] = 0
                srv["status"] = "UP"
            else:
                srv["misses"] += 1
                if srv["misses"] >= MAX_MISSES:
                    if srv["status"] != "DOWN":
                        print(f"[FaultMonitor] Server {srv['id']} is DOWN")
                        srv["status"] = "DOWN"
        time.sleep(PING_INTERVAL)

def start():
    t = threading.Thread(target=_monitor_loop, daemon=True)
    t.start()

def get_status():
    return {s["id"]: s["status"] for s in SERVERS}

def get_live_servers():
    return [s for s in SERVERS if s["status"] == "UP"]