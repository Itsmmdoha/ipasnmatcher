from .exceptions import InvalidASNError
from datetime import datetime, timezone


def _validate_asn(asn: str) -> str:
    """Validate ASN format."""
    asn = asn.upper()
    if asn.startswith('AS'):
        asn_number = asn[2:]
    else:
        asn_number = asn
        asn = f'AS{asn_number}'
    try:
        asn_int = int(asn_number)
        if asn_int <= 0 or asn_int > 4294967295:
            raise InvalidASNError(f"ASN number {asn_int} is invalid")
    except ValueError:
        raise InvalidASNError(f"Invalid ASN format: {asn}")
    
    return asn

def is_prefix_active(timelines) -> bool:
    """Check if at least one prefix timeline is currently active."""
    now = datetime.now(timezone.utc)
    for t in timelines:
        end_time = datetime.fromisoformat(t["endtime"])
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        if end_time > now:
            return True  # at least one active period
    return False  # all ended
