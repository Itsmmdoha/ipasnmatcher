from requests import get
from json import loads
from ipaddress import ip_address, ip_network

ASN = "AS151981"
# RIPEstat API
res = get("https://stat.ripe.net/data/announced-prefixes/data.json?resource="+ASN)

data = loads(res.text)

prefixes = [prefix for prefix in data["data"]["prefixes"]]

ip = input("enter an ip: ")

flag = False
for prefix in prefixes:
    network = ip_network(prefix["prefix"], strict=False)
    address = ip_address(ip)
    if address in network:
        flag = True
        break
print(flag)
