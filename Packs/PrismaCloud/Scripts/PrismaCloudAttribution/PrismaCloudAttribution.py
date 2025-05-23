import demistomock as demisto
from CommonServerPython import *  # noqa # pylint: disable=unused-wildcard-import

from CommonServerUserPython import *  # noqa

"""PrismaCloudAttribution

"""


from collections.abc import Iterable
from typing import Any

IPADDRESS_KEYS = ["publicIpAddress", "natIP", "publicIp", "inboundIpAddress", "ipAddress", "IPAddress"]
FQDN_KEYS = [
    "publicDnsName",
    "dnsname",
    "domainName",
    "name",
    "dnsName",
    "hostName",
    "properties.hostName",
    "fqdn",
    "enabledHostNames",
    "web",
]

""" STANDALONE FUNCTION """


def recursive_find(keys: list[str] | str, value: Iterable[Any]) -> Iterable[Any]:
    if not isinstance(keys, list):
        keys = [keys]
    for k, v in value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else []:
        if k in keys:
            yield v
        elif isinstance(v, list):
            for result in recursive_find(keys, v):
                yield result
        elif isinstance(v, dict):
            for result in recursive_find(keys, v):
                yield result


def handle_data(data: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    out_dict: dict = {}
    if "ip" in fields:
        ips = list(set(recursive_find(IPADDRESS_KEYS, data)))
        out_dict["ip"] = ips if ips else None
    if "fqdn" in fields:
        fqdns = list({fq for fq in recursive_find(FQDN_KEYS, data) if fq.count(".") > 0})
        out_dict["fqdn"] = fqdns if fqdns else None
    return out_dict


""" COMMAND FUNCTION """


def attribution_command(args: dict[str, Any]) -> CommandResults:
    assets = argToList(args.get("assets", []))
    fields = argToList(
        args.get("fields", "id,cloudType,resourceName,resourceType,regionId,accountId,accountName,hasAlert,service,ip,fqdn")
    )

    asset_dict: dict[str, dict[str, Any]] = {}

    for asset in assets:
        if not isinstance(asset, dict):
            continue
        if "rrn" not in asset:
            continue
        rrn = asset["rrn"]
        asset_dict[rrn] = {"rrn": rrn}
        for k in asset:
            if k == "name" and "resourceName" in fields:
                asset_dict[rrn]["resourceName"] = asset["name"]
            elif k == "data" and isinstance(asset[k], dict):
                asset_dict[rrn].update(handle_data(asset[k], fields))
            elif k in fields:
                asset_dict[rrn][k] = asset[k]

    return CommandResults(outputs=list(asset_dict.values()), outputs_prefix="PrismaCloud.Attribution", outputs_key_field="rrn")


""" MAIN FUNCTION """


def main():
    try:
        return_results(attribution_command(demisto.args()))
    except Exception as ex:
        return_error(f"Failed to execute PrismaCloudAttribution. Error: {ex!s}")


""" ENTRY POINT """


if __name__ in ("__main__", "__builtin__", "builtins"):
    main()
