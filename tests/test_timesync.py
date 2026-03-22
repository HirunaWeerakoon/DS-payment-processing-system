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


