from requests import get
from ipaddress import ip_address, ip_network
import json
from time import time
from datetime import datetime, timezone
from os import makedirs

def is_prefix_active(timelines):
    now = datetime.now(timezone.utc)
    for t in timelines:
        end_time = datetime.fromisoformat(t["endtime"])
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        if end_time > now:
            return True  # at least one active period
    return False  # all ended

class ASN:
    def __init__(self,asn: str,strict: bool = False, cache_max_age: int = 3600):
        self.asn = asn
        self._strict = strict
        self._cache_max_age = cache_max_age
        self._SOURCE_APP: str = "Ipasnmatcher"
        self._network_objects = []
        makedirs(".ipasnmatcher_cache", exist_ok=True)
        self._load()

    def _fetch_from_api(self):
        api_url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={self.asn}&sourceapp={self._SOURCE_APP}"
        res = get(api_url)
        data = json.loads(res.text)
        prefix_list = data["data"]["prefixes"]
        return prefix_list

    def _write_to_cache(self, prefix_list):
        cache_data = {
            "asn": self.asn,
            "timestamp": int(time()), 
            "prefix_list": prefix_list
        }
        with open(file=f".ipasnmatcher_cache/{self.asn}.json",mode="w") as f:
            json.dump(cache_data, f, indent=4)

    def _fetch_from_cache(self):
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

    def _load(self):
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

    def match_asn(self, ip: str) -> bool:
        address = ip_address(ip)
        flag = any(address in net for net in self._network_objects)
        return flag
