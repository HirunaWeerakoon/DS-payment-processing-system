import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

import time
import time_sync
from time_sync import now, correct_timestamp, sync_clock

def test_now_returns_float():
    result = now()
    assert isinstance(result, float)
    assert abs(result - time.time()) < 5

def test_correct_timestamp_applies_offset():
    time_sync._offset = 2.0
    corrected = correct_timestamp(1000.0)
    assert corrected == 1002.0
    time_sync._offset = 0.0

def test_sync_clock_does_not_crash():
    try:
        sync_clock()
    except Exception as e:
        assert False, f"sync_clock raised an exception: {e}"

# --- NEW TESTS  ---
from log_ordering import add_to_buffer, get_ordered_logs, _buffer
from log_ordering import flush_to_ledger

def setup_function():
    """Clear the buffer before each log ordering test."""
    _buffer.clear()

def test_add_to_buffer_corrects_timestamp():
    """add_to_buffer applies NTP offset to incoming timestamp."""
    time_sync._offset = 5.0
    payment = {'id': 'abc', 'timestamp': 1000.0, 'amount': 10}
    add_to_buffer(payment)
    assert _buffer[0]['timestamp'] == 1005.0
    time_sync._offset = 0.0

def test_get_ordered_logs_sorts_by_timestamp():
    """get_ordered_logs returns payments sorted oldest first."""
    _buffer.clear()
    time_sync._offset = 0.0
    _buffer.append({'id': '1', 'timestamp': 3000.0})
    _buffer.append({'id': '2', 'timestamp': 1000.0})
    _buffer.append({'id': '3', 'timestamp': 2000.0})
    ordered = get_ordered_logs()
    times = [p['timestamp'] for p in ordered]
    assert times == sorted(times)

def test_flush_to_ledger_clears_buffer():
    """flush_to_ledger writes payments and empties the buffer."""
    _buffer.clear()
    _buffer.append({'id': 'x', 'timestamp': 1000.0})
    recorded = []
    flush_to_ledger(lambda p: recorded.append(p))
    assert len(recorded) == 1
    assert len(_buffer) == 0

def test_now_is_greater_than_zero():
    """now() always returns a positive timestamp."""
    assert now() > 0
