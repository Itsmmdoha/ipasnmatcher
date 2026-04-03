class IPASNMatcherError(Exception):
    """Base exception for IPASNMatcher"""
    pass

class InvalidASNError(IPASNMatcherError):
    """Raised when an invalid ASN is provided"""
    pass

class NetworkError(IPASNMatcherError):
    """Raised when network/API requests fail"""
    pass
