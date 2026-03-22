from time_sync import correct_timestamp

_buffer = []  # holds payments waiting to be ordered

def add_to_buffer(payment):
    """Add an incoming payment to the ordering buffer."""
    payment['timestamp'] = correct_timestamp(payment['timestamp'])
    _buffer.append(payment)

def get_ordered_logs():
    """Return all buffered payments sorted by corrected timestamp."""
    return sorted(_buffer, key=lambda p: p['timestamp'])

def flush_to_ledger(record_fn):
    """Write ordered payments to the ledger and clear the buffer."""
    ordered = get_ordered_logs()
    for p in ordered:
        record_fn(p)
    _buffer.clear()
    return len(ordered)