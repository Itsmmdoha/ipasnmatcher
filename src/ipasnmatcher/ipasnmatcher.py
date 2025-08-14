from requests import get, Timeout, RequestException
from ipaddress import AddressValueError, ip_address, ip_network
import json
from time import time
from os import makedirs
from .exceptions import InvalidIPError, NetworkError
from .utils import _validate_asn, is_prefix_active


class ASN:
    """
    Represents an Autonomous System Number (ASN).

    The class fetches prefix data from the RIPEstat API and caches it locally.

    Parameters
    ----------
    asn : str
        ASN identifier (e.g., "AS15169").

    strict : bool, optional
        If True, only prefixes that are currently active will be included.

    cache_max_age : int, optional
        Maximum cache lifetime in seconds (default is 3600).

    Raises
    ------
    InvalidASNError
        If the provided ASN is invalid.
    NetworkError
        If data fetching for ASN fail or timeout.
    """
    def __init__(self,asn: str,strict: bool = False, cache_max_age: int = 3600):
        self.asn = _validate_asn(asn) 
        self._strict = strict
        self._cache_max_age = cache_max_age
        self._SOURCE_APP: str = "Ipasnmatcher"
        self._network_objects = []
        makedirs(".ipasnmatcher_cache", exist_ok=True)
        self._load()
        self.asn_repr = f"ASN(asn={self.asn!r}, strict={self._strict!r}, cache_max_age={self._cache_max_age!r} )"

    def __add__(self, other):
        self._network_objects.extend(other._network_objects)
        self.asn_repr = f"{self.asn_repr} + {other.asn_repr}"
        return self
    def __repr__(self) -> str:
        return self.asn_repr

    def _fetch_from_api(self):
        """Fetch prefix data for the ASN from RIPEstat API."""
        api_url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={self.asn}&sourceapp={self._SOURCE_APP}"
        try:
            res = get(api_url)
        except Timeout:
            raise NetworkError(f"Request timed out while fetching data for ASN {self.asn}")
        except RequestException as e:
            raise NetworkError(f"Failed to fetch data for ASN {self.asn}: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise NetworkError(f"Invalid data received for ASN {self.asn}")
        data = res.json()
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
        ip : str
            IPv4 or IPv6 address to check.

        Returns
        -------
        bool
            True if the IP belongs to one of the ASN's prefixes, False otherwise.

        Raises
        ------
        InvalidIPError
            If the provided IP address format is invalid.
        """
        try:
            address = ip_address(ip)
        except AddressValueError:
            raise InvalidIPError(f"Invalid IP address: {ip}")
        flag = any(address in net for net in self._network_objects)
        return flag
