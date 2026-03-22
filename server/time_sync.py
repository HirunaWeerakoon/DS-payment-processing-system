import ntplib, time

NTP_SERVER = 'pool.ntp.org'
_offset = 0.0  # difference between local clock and NTP clock

def sync_clock():
    """Fetch NTP time and calculate the offset. Call this on server startup."""
    global _offset
    try:
        c = ntplib.NTPClient()
        response = c.request(NTP_SERVER, version=3)
        _offset = response.offset
        print(f'[TimeSync] Clock offset: {_offset:.4f}s')
    except Exception as e:
        print(f'[TimeSync] NTP failed, using local clock: {e}')
        _offset = 0.0

def now():
    """Return NTP-corrected current time as Unix timestamp."""
    return time.time() + _offset

def correct_timestamp(raw_ts):
    """Apply NTP offset to a timestamp received from another server."""
    return raw_ts + _offset