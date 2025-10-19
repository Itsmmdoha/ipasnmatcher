# ipasnmatcher

A Python package to verify if an IP address belongs to a specific ASN's network ranges using RIPEstat data.

## Features

* Lazy loads prefix data on first match for faster initialization
* Fast IP-to-ASN matching with optimized network range checks
* Built-in caching to minimize API requests
* Optional strict mode to consider only active prefixes
* Uses accurate data from RIPE NCC
* Supports both synchronous and asynchronous usage

## Installation

```bash
pip install ipasnmatcher
```

## Usage

### Synchronous Example

```python
from ipasnmatcher import ASN

# Create an ASN object (prefix data will be lazy-loaded on first match)
asn = ASN("AS151981")

# The first match triggers data loading from RIPEstat API (and caches it)
print(asn.match("153.53.148.45"))  # True or False
```

### Asynchronous Example

```python
import asyncio
from ipasnmatcher import AsyncASN

async def main():
    # Create an async ASN object (lazy-loads on first async_match)
    async_asn = AsyncASN("AS15169")

    # The first async_match call triggers async data loading
    result = await async_asn.async_match("8.8.8.8")
    print(result)  # True or False

asyncio.run(main())
```

## Advanced Usage

```python
asn = ASN(
    asn="AS15169",      # ASN (e.g., Google)
    strict=True,        # Only consider active prefixes
    cache_max_age=7200  # Cache duration in seconds (2 hours)
)
```

### Combining ASN Objects

You can combine multiple ASNs using the `+` operator.
When combined:

* If **any** of the ASNs has `strict=True`, the resulting combined ASN will also be **strict**.
* The combined ASN’s `max_cache_age` will be the **minimum** of the values from the ASNs being merged.

```python
from ipasnmatcher import ASN

google = ASN("AS15169", strict=False, cache_max_age=7200)
cloudflare = ASN("AS13335", strict=True, cache_max_age=3600)

combined = google + cloudflare

# Combined inherits strict=True and cache_max_age=3600
print(combined.match("8.8.8.8"))   # True (Google)
print(combined.match("1.1.1.1"))   # True (Cloudflare)
```

`repr()` shows the full combination:

```
ASN(asn='AS15169', strict=False, cache_max_age=7200) + ASN(asn='AS13335', strict=True, cache_max_age=3600)
```

## Parameters

```python
ASN(asn: str, strict: bool = False, cache_max_age: int = 3600)
```

* `asn`: ASN identifier in format `"AS12345"`
* `strict`: If `True`, only prefixes currently active are considered (default: `False`)
* `cache_max_age`: Cache lifetime in seconds (default: `3600`)

## How it works

* Data is **lazy-loaded** — the first `match()` or `async_match()` triggers prefix loading from the RIPEstat API.
* Prefix data is cached locally in `.ipasnmatcher_cache/{asn}.json`.
* Subsequent matches use cached data if it’s fresh (not older than `cache_max_age`).
* Matching is done efficiently using Python’s `ipaddress` module.

## Use Cases

* Network security and traffic validation
* CDN traffic routing based on ASN ownership
* IP classification by network operators
* Compliance monitoring of network connections

## GitHub

Star or fork this project on [GitHub](https://github.com/Itsmmdoha/ipasnmatcher).

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Itsmmdoha/ipasnmatcher/blob/main/LICENSE) file for details.
