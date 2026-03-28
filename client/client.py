# client/client.py
import requests
import random
import time
import threading

SERVERS = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003",
]

NAMES = ["alice", "bob", "carol", "dave", "eve", "frank"]

def send_payment(sender, receiver, amount, server_url):
    try:
        r = requests.post(
            f"{server_url}/pay",
            json={"sender": sender, "receiver": receiver, "amount": amount},
            timeout=5
        )
        data = r.json()
        print(f"[OK] {sender} -> {receiver} £{amount:.2f} | id={data['id'][:8]}... | server={data['server']}")
        return data
    except Exception as e:
        print(f"[FAIL] {server_url} -> {e}")
        return None

def run_sequential(n=10):
    """Send n payments one after another to Server A."""
    print(f"\n--- Sequential test: {n} payments to Server A ---")
    for _ in range(n):
        sender   = random.choice(NAMES)
        receiver = random.choice([x for x in NAMES if x != sender])
        amount   = round(random.uniform(5, 500), 2)
        send_payment(sender, receiver, amount, SERVERS[0])
        time.sleep(0.2)

def run_concurrent(n=10):
    """Send n payments simultaneously across all 3 servers."""
    print(f"\n--- Concurrent test: {n} payments across all servers ---")
    threads = []
    for i in range(n):
        sender   = random.choice(NAMES)
        receiver = random.choice([x for x in NAMES if x != sender])
        amount   = round(random.uniform(5, 500), 2)
        server   = SERVERS[i % 3]   # round-robin across servers
        t = threading.Thread(
            target=send_payment,
            args=(sender, receiver, amount, server)
        )
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

def run_failover_test():
    """
    Failover test — keep sending payments.
    Kill a server manually during this test to see failover in action.
    """
    print("\n--- Failover test: sending payments every second ---")
    print("    Kill one of the servers now to see failover!")
    print("    Press Ctrl+C to stop.\n")
    i = 0
    while True:
        sender   = random.choice(NAMES)
        receiver = random.choice([x for x in NAMES if x != sender])
        amount   = round(random.uniform(5, 500), 2)
        server   = SERVERS[i % 3]
        send_payment(sender, receiver, amount, server)
        i += 1
        time.sleep(1)

if __name__ == "__main__":
    print("Choose a test:")
    print("  1. Sequential (10 payments to Server A)")
    print("  2. Concurrent (10 payments across all servers)")
    print("  3. Failover   (continuous — kill a server to test)")
    choice = input("\nEnter 1, 2 or 3: ").strip()

    if choice == "1":
        run_sequential(10)
    elif choice == "2":
        run_concurrent(10)
    elif choice == "3":
        run_failover_test()
    else:
        print("Invalid choice")