# ipasnmatcher

A Python package that allows you to verify if an IP address belongs to a specific ASN's network ranges.

## Features

- 🚀 Fast IP-to-ASN matching using optimized network ranges
- 💾 Built-in caching to minimize API calls
- 🎯 Strict mode for active prefixes only
- 🌐 Uses RIPE NCC data for accurate results

## Installation

```bash
git clone https://github.com/itsmmdoha/ipasnmatcher
cd ipasnmatcher
```

## Usage

```python
from ipasnmatcher import ASN

# Create an ASN object
asn = ASN(asn="AS151981")

# Check if an IP belongs to this ASN
print(asn.match("153.53.148.45"))  # True or False
```

### Advanced Usage

```python
from ipasnmatcher import ASN

# Configure with options
asn = ASN(
    asn="AS15169",           # Google's ASN
    strict=True,             # Only active prefixes
    cache_max_age=7200       # Cache for 2 hours
)

# Test multiple IPs
test_ips = ["8.8.8.8", "1.1.1.1", "172.217.14.142"]

for ip in test_ips:
    if asn.match(ip):
        print(f" {ip} belongs to AS15169")
    else:
        print(f" {ip} does not belong to AS15169")
```

## Use Cases

- **Network Security**: Verify if traffic originates from expected ASNs
- **CDN Optimization**: Route traffic based on ASN ownership
- **IP Intelligence**: Classify IPs by their network operators
- **Compliance Monitoring**: Ensure connections come from approved networks

## Parameters

```python
ASN(asn, strict=False, cache_max_age=3600)
```

- **`asn`**: ASN number (format: "AS12345")
- **`strict`**: Only consider currently active prefixes (default: False)
- **`cache_max_age`**: Cache duration in seconds (default: 3600)

## License

MIT License
