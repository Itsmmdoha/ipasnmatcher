from httpx import get, AsyncClient, ConnectTimeout, ReadTimeout, RequestError
from ipaddress import AddressValueError, ip_address, ip_network
import json
from time import time
from os import makedirs
from .exceptions import InvalidIPError, NetworkError
from .utils import _validate_asn, is_prefix_active


class ASN:
    """
    Represents an Autonomous System Number (ASN).

    The class lazy loads prefix data from the RIPEstat API and caches it locally.

    Example
    ----------
        ```python
        asn = ASN("AS15169")
        match = asn.match("
        ```

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
        self._asn_list = [_validate_asn(asn)] 
        self._strict = strict
        self._cache_max_age = cache_max_age
        self._SOURCE_APP: str = "Ipasnmatcher"
        self._network_objects = []
        makedirs(".ipasnmatcher_cache", exist_ok=True)
        self._last_loaded = int(time())
        self.asn_repr = f"ASN(asn={self._asn_list!r}, strict={self._strict!r}, cache_max_age={self._cache_max_age!r} )"

    def __add__(self, other):
        if type(self) is not type(other):
            raise TypeError("Can only add ASN objects of the same class")
        self._asn_list += other._asn_list
        self._network_objects += other._network_objects
        if other._strict == True: self._strict = True
        self._cache_max_age = min(self._cache_max_age,other._cache_max_age)
        self._last_loaded = min(self._last_loaded, other._last_loaded)
        self._load()
        return self
    def __repr__(self) -> str:
        asn_repr = ""
        for asn in self._asn_list:
            asn_repr += f" ASN(asn={asn!r}, strict={self._strict!r}, cache_max_age={self._cache_max_age!r} )"
        return asn_repr

    def _fetch_from_api(self,asn):
        """Fetch prefix data for the ASN from RIPEstat API."""
        api_url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}&sourceapp={self._SOURCE_APP}"
        try:
            res = get(api_url)
            res.raise_for_status()
        except(ConnectTimeout, ReadTimeout):
            raise NetworkError(f"Request timed out while fetching data for ASN {asn}")
        except RequestError as e:
            raise NetworkError(f"Failed to fetch data for ASN {asn}: {str(e)}")
        data = res.json()
        prefix_list = data["data"]["prefixes"]
        return prefix_list

    def _write_to_file_cache(self, asn, prefix_list) -> None:
        """Save prefix data to local cache file in the `.ipasnmatcher_cache` directory."""
        cache_data = {
            "asn": asn,
            "timestamp": int(time()), 
            "prefix_list": prefix_list
        }
        with open(file=f".ipasnmatcher_cache/{asn}.json",mode="w") as f:
            json.dump(cache_data, f, indent=4)

    def _fetch_from_file_cache(self,asn):
        """Fetch prefix data for the ASN from cache file."""
        try:
            with open(file=f".ipasnmatcher_cache/{asn}.json",mode="r") as f:
                cache_data = json.load(f)
                if time() - cache_data["timestamp"] > self._cache_max_age:
                    return None
                return cache_data["prefix_list"]
        except FileNotFoundError:
            return None
        except (KeyError, json.JSONDecodeError):
            return None

    def _load_to_network_objects(self, prefix_list):
        """
        Core logic to process prefix_list into _network_objects.
            `_network_objects` is a list of `ipaddress.IPv4Network` or
            `ipaddress.IPv6Network` instances representing the ASN's announced prefixes.

        """
        network_objects = []
        for prefix in prefix_list:
            timelines = prefix["timelines"]
            if self._strict and not is_prefix_active(timelines):
                continue
            network_objects.append(ip_network(prefix["prefix"], strict=False))
        self._network_objects += network_objects 

    def _load(self) -> None:
        """
        Load ASN prefix data (from cache or API) and build `_network_objects`.

        """
        for asn in self._asn_list:
            prefix_list = self._fetch_from_file_cache(asn=asn)
            if prefix_list is None:
                prefix_list = self._fetch_from_api(asn=asn)
                if prefix_list:
                    self._write_to_file_cache(asn=asn, prefix_list=prefix_list)
            self._load_to_network_objects(prefix_list=prefix_list)
        self._last_loaded = int(time())

    def is_ip_in_prefix_list(self, ip: str) -> bool:
        """Core logic to check if an IP has a match in the prefix list."""
        try:
            address = ip_address(ip)
        except (AddressValueError, ValueError):
            raise InvalidIPError(f"Invalid IP address: {ip}")
        flag = any(address in net for net in self._network_objects)
        return flag

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
        if not self._network_objects or time() - self._last_loaded > self._cache_max_age:
            self._load()
        return self.is_ip_in_prefix_list(ip=ip)



class AsyncASN(ASN):
    """
    Represents an Asynchronous Autonomous System Number (ASN).

    The class asynchronously lazy loads prefix data from the RIPEstat API and caches it locally.

    The class supports both context-managed and manual usage patterns:

    Examples
    --------
    Async context manager:

        ```python
        async with AsyncASN("AS15169") as asn:
            match = await asn.async_match("8.8.8.8")
        ```

    Manual lifecycle:

        ```python
        asn = AsyncASN("AS15169")
        match = await asn.async_match("8.8.8.8")
        await asn.aclose()
        ```

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
    def __init__(self, asn: str, strict: bool = False, cache_max_age: int = 3600):
        super().__init__(asn, strict, cache_max_age)
        self._client: AsyncClient | None = None
    async def __aenter__(self):
        self._client = AsyncClient()
        await self._load_async()
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
        return False
    async def aclose(self):
        """
        Close any underlying asynchronous resources.

        This method should be called when the instance is used without an
        asynchronous context manager (`async with`). It ensures that any
        open connections are properly closed and resources released.
        """
        if self._client:
            await self._client.aclose()
            self._client = None


    async def _fetch_from_api_async(self,asn):
        if not self._client:
            self._client = AsyncClient()
        api_url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}&sourceapp={self._SOURCE_APP}"
        try:
            res= await self._client.get(api_url)
            res.raise_for_status()
        except(ConnectTimeout, ReadTimeout):
            raise NetworkError(f"Request timed out while fetching data for ASN {self._asn_list}")
        except RequestError as e:
            raise NetworkError(f"Failed to fetch data for ASN {self._asn_list}: {str(e)}")
        data = res.json()
        prefix_list = data["data"]["prefixes"]
        return prefix_list

    async def _load_async(self):
        """
        Load ASN prefix data Asynchronously (from cache or API) and build `_network_objects`.

        `_network_objects` is a list of `ipaddress.IPv4Network` or
        `ipaddress.IPv6Network` instances representing the ASN's announced prefixes.
        """
        for asn in self._asn_list:
            prefix_list = self._fetch_from_file_cache(asn=asn)
            if prefix_list is None:
                prefix_list = await self._fetch_from_api_async(asn=asn)
                if prefix_list:
                    self._write_to_file_cache(asn=asn, prefix_list=prefix_list)
            self._load_to_network_objects(prefix_list=prefix_list)
        self._last_loaded = int(time())

    async def async_match(self, ip: str) -> bool:
        """
        Asynchronously check if an IP belongs to the ASN's announced prefixes.

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
        if not self._network_objects or time() - self._last_loaded > self._cache_max_age:
            await self._load_async()
        return self.is_ip_in_prefix_list(ip=ip)

