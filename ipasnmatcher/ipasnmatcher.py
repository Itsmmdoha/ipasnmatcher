from requests import get
from ipaddress import ip_address, ip_network
import json
from time import time
from datetime import datetime, timezone
from os import makedirs

def is_prefix_active(timelines):
    """Check if at least one prefix timeline is currently active."""
    now = datetime.now(timezone.utc)
    for t in timelines:
        end_time = datetime.fromisoformat(t["endtime"])
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        if end_time > now:
            return True  # at least one active period
    return False  # all ended

class ASN:
    """
    Represents an Autonomous System Number (ASN).

    The class fetches prefix data from the RIPEstat API and caches it locally.

    Parameters
    ----------
    `asn : str`
        ASN identifier (e.g., "AS15169").

    `strict : bool`  optional
        If True, only prefixes that are currently active will be included.

    `cache_max_age : int` optional
        Maximum cache lifetime in seconds (default is 3600).
    """
    def __init__(self,asn: str,strict: bool = False, cache_max_age: int = 3600):
        self.asn = asn
        self._strict = strict
        self._cache_max_age = cache_max_age
        self._SOURCE_APP: str = "Ipasnmatcher"
        self._network_objects = []
        makedirs(".ipasnmatcher_cache", exist_ok=True)
        self._load()

    def _fetch_from_api(self):
        """Fetch prefix data for the ASN from RIPEstat API."""
        api_url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={self.asn}&sourceapp={self._SOURCE_APP}"
        res = get(api_url)
        res.raise_for_status()
        data = json.loads(res.text)
        prefix_list = data["data"]["prefixes"]
        return prefix_list

    def _write_to_cache(self, prefix_list) -> None:
        """Save prefix data to local cache file in the `.ipasnmatcher_cache` directory."""
        cache_data = {
            "asn": self.asn,
            "timestamp": int(time()), 
            "prefix_list": prefix_list
        }
        with open(file=f".ipasnmatcher_cache/{self.asn}.json",mode="w") as f:
            json.dump(cache_data, f, indent=4)

    def _fetch_from_cache(self):
        """Fetch prefix data for the ASN from cache file."""
        try:
            with open(file=f".ipasnmatcher_cache/{self.asn}.json",mode="r") as f:
                cache_data = json.load(f)
                if time() - cache_data["timestamp"] > self._cache_max_age:
                    return None
                return cache_data["prefix_list"]
        except FileNotFoundError:
            return None
        except (KeyError, json.JSONDecodeError):
            return None

    def _load(self) -> None:
        """
        Load ASN prefix data (from cache or API) and build `_network_objects`.

        `_network_objects` is a list of `ipaddress.IPv4Network` or
        `ipaddress.IPv6Network` instances representing the ASN's announced prefixes.
        """
        prefix_list = self._fetch_from_cache()
        if prefix_list is None:
            prefix_list = self._fetch_from_api()
            if prefix_list:
                self._write_to_cache(prefix_list)
        network_objects = []
        for prefix in prefix_list:
            timelines = prefix["timelines"]
            if self._strict and not is_prefix_active(timelines):
                continue
            network_objects.append(ip_network(prefix["prefix"], strict=False))
        self._network_objects = network_objects 

    def match(self, ip: str) -> bool:
        """
        Check if an IP belongs to the ASN's announced prefixes.

        Parameters
        ----------
        `ip : str`
            IPv4 or IPv6 address to check.

        Returns
        -------
        bool
            True if the IP belongs to one of the ASN's prefixes, False otherwise.
        """
        address = ip_address(ip)
        flag = any(address in net for net in self._network_objects)
        return flag
