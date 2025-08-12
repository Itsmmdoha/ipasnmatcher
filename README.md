# ipasnmatcher

A Python package to verify if an IP address belongs to a specific ASN's network ranges using RIPEstat data.

## Features

* Fast IP-to-ASN matching with optimized network ranges
* Built-in caching to minimize API requests
* Optional strict mode to consider only active prefixes
* Uses accurate data from RIPE NCC

## Installation

```bash
pip install ipasnmatcher
```

## Usage

```python
from ipasnmatcher import ASN

# Creating an ASN object fetches prefix data from the RIPEstat API and caches it locally
asn = ASN(asn="AS151981")

# Check if an IP belongs to this ASN
print(asn.match("153.53.148.45"))  # True or False
```

## Advanced Usage

```python
asn = ASN(
    asn="AS15169",      # ASN (e.g., Google)
    strict=True,        # Only consider active prefixes
    cache_max_age=7200  # Cache duration in seconds (2 hours)
)

ips = ["8.8.8.8", "1.1.1.1", "172.217.14.142"]
for ip in ips:
    if asn.match(ip):
        print(f"{ip} belongs to {asn.asn}")
    else:
        print(f"{ip} does not belong to {asn.asn}")
```

## Parameters

```python
ASN(asn: str, strict: bool = False, cache_max_age: int = 3600)
```

* `asn`: ASN identifier in format `"AS12345"`
* `strict`: If `True`, only prefixes currently active are considered (default: `False`)
* `cache_max_age`: Cache lifetime in seconds (default: `3600`)

## How it works

* On initialization, the `ASN` object fetches announced prefixes from the RIPEstat API and caches them locally in `.ipasnmatcher_cache/{asn}.json`.
* Subsequent uses load data from cache if it is fresh (not older than `cache_max_age`).
* Matching IPs against ASN prefixes is done efficiently using Python's `ipaddress` module.

## Use Cases

* Network security and traffic validation
* CDN traffic routing based on ASN ownership
* IP classification by network operators
* Compliance monitoring of network connections

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
