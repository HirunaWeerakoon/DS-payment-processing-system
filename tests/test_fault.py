# tests/test_fault.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

import fault_monitor
from fault_monitor import get_status, get_live_servers, SERVERS

def reset_servers():
    for s in SERVERS:
        s['status'] = 'UP'
        s['misses'] = 0

def test_all_servers_start_as_up():
    reset_servers()
    status = get_status()
    assert status['A'] == 'UP'
    assert status['B'] == 'UP'
    assert status['C'] == 'UP'

def test_server_marked_down_after_max_misses():
    reset_servers()
    SERVERS[0]['misses'] = fault_monitor.MAX_MISSES
    SERVERS[0]['status'] = 'DOWN'
    status = get_status()
    assert status['A'] == 'DOWN'

def test_get_live_servers_excludes_down():
    reset_servers()
    SERVERS[0]['status'] = 'DOWN'
    live = get_live_servers()
    ids = [s['id'] for s in live]
    assert 'A' not in ids
    assert 'B' in ids
    assert 'C' in ids

def test_get_live_servers_empty_when_all_down():
    for s in SERVERS:
        s['status'] = 'DOWN'
    assert get_live_servers() == []
    reset_servers()

def test_server_recovers_when_misses_reset():
    reset_servers()
    SERVERS[1]['status'] = 'DOWN'
    SERVERS[1]['misses'] = 5
    SERVERS[1]['status'] = 'UP'
    SERVERS[1]['misses'] = 0
    status = get_status()
    assert status['B'] == 'UP'

def test_ping_interval_value():
    assert fault_monitor.PING_INTERVAL == 2

def test_max_misses_value():
    assert fault_monitor.MAX_MISSES == 3