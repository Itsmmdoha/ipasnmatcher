import pytest
from ipasnmatcher import ASN, InvalidIPError, InvalidASNError

class TestASN:
    def test_valid_match(self):
        """Test matching a known IP to its ASN"""
        asn = ASN("AS15169")  # Google
        assert asn.match("8.8.8.8") == True
    
    def test_invalid_match(self):
        """Test IP that doesn't belong to ASN"""
        asn = ASN("AS15169")  # Google
        assert asn.match("1.1.1.1") == False  # Cloudflare IP
    
    def test_invalid_ip_format(self):
        """Test invalid IP format raises exception"""
        asn = ASN("AS15169")
        with pytest.raises(InvalidIPError):
            asn.match("invalid.ip.address")
    
    def test_invalid_asn_format(self):
        """Test invalid ASN format raises exception"""
        with pytest.raises(InvalidASNError):
            ASN("INVALID_ASN")

if __name__ == "__main__":
    # Simple test runner for development
    test = TestASN()
    test.test_valid_match()
    test.test_invalid_match()
    print("Basic tests passed!")
