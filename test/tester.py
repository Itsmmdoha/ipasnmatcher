import pytest
from ipasnmatcher import ASN, InvalidIPError, InvalidASNError

# --- Fixtures / helpers ---
@pytest.fixture
def fake_prefixes():
    return [
        {"prefix": "8.8.8.0/24", "timelines": []},      # Google (AS15169)
        {"prefix": "1.1.1.0/24", "timelines": []},      # Cloudflare (AS13335)
    ]


@pytest.fixture
def patched_asn(monkeypatch, fake_prefixes):
    """Patch ASN._fetch_from_api to avoid real network calls."""
    def fake_fetch(_self):
        return fake_prefixes

    monkeypatch.setattr(ASN, "_fetch_from_api", fake_fetch)
    return ASN("AS15169")  # uses patched data instead of API


# --- Tests ---
class TestASN:
    def test_valid_match(self, patched_asn):
        """IP inside 8.8.8.0/24 should match"""
        assert patched_asn.match("8.8.8.8") is True

    def test_invalid_match(self, patched_asn):
        """IP not in AS15169 prefixes should not match"""
        assert patched_asn.match("9.9.9.9") is False

    def test_invalid_ip_format(self, patched_asn):
        """Invalid IP raises InvalidIPError"""
        with pytest.raises(InvalidIPError):
            patched_asn.match("invalid.ip.address")

    def test_invalid_asn_format(self):
        """Bad ASN format raises InvalidASNError"""
        with pytest.raises(InvalidASNError):
            ASN("INVALID_ASN")

    def test_repr(self, patched_asn):
        """Ensure __repr__ works as expected"""
        rep = repr(patched_asn)
        assert "ASN(asn='AS15169'" in rep

    def test_add_operator(self, patched_asn, monkeypatch):
        """Test combining ASN objects with +"""
        # New ASN object for Cloudflare
        other = ASN("AS13335")

        # Patch the fetcher for second ASN
        monkeypatch.setattr(
            ASN, "_fetch_from_api", lambda _self: [{"prefix": "1.1.1.0/24", "timelines": []}]
        )
        other._load()

        combined = patched_asn + other
        assert combined.match("8.8.8.8") is True
        assert combined.match("1.1.1.1") is True


if __name__ == "__main__":
    import sys, pytest
    sys.exit(pytest.main([__file__]))
