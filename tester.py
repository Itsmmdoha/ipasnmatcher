from ipasnmatcher import ASN

asn = ASN(asn="AS151981", strict=False)

print(asn.match_asn("153.53.148.45"))
