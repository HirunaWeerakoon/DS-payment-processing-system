# server/replication.py
import requests

# The other two nodes in the cluster [cite: 298-301]
PEER_URLS = [
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003"
]

def replicate_to_peers(payment):
    """Broadcasts the payment to peers for primary-backup replication [cite: 302-303]"""
    results = []
    for url in PEER_URLS:
        try:
            # Pushing to the /replicate endpoint of peers [cite: 308-311]
            r = requests.post(
                url + "/replicate",
                json=payment,
                timeout=2
            )
            results.append({'url': url, 'ok': r.status_code == 200})
        except Exception as e:
            # Handles if a peer is down [cite: 313-317]
            results.append({'url': url, 'ok': False, 'error': str(e)})
    return results