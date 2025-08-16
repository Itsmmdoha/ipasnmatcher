# ipasnmatcher

<img width="6749" height="4036" alt="ipasnmatcher-min" src="https://github.com/user-attachments/assets/22ae405f-e4ec-4a51-ad53-c040a02e4cc9" />

Verify if an IP address belongs to an ASN’s network ranges with research-grade data from RIPEstat.

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

```

### Combine ASN objects

Merge multiple ASNs with `+` to check IPs against all their prefixes:

```python
from ipasnmatcher import ASN

google = ASN("AS15169")      # Google
cloudflare = ASN("AS13335")  # Cloudflare

combined = google + cloudflare
print(combined.match("8.8.8.8"))   # True (Google)
print(combined.match("1.1.1.1"))   # True (Cloudflare)
```

`repr()` shows the full combination:

```
ASN(asn='AS15169', strict=False, cache_max_age=3600) + ASN(asn='AS13335', strict=False, cache_max_age=3600)
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

## GitHub

Star or fork this project on [GitHub](https://github.com/Itsmmdoha/ipasnmatcher).

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Itsmmdoha/ipasnmatcher/blob/main/LICENSE) file for details.
