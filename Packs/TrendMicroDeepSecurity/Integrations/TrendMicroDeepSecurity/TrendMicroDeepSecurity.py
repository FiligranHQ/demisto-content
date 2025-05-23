from collections.abc import Callable
from typing import Any, get_args, get_origin, get_type_hints, no_type_check

import demistomock as demisto
import urllib3
from CommonServerPython import *
from requests.exceptions import ConnectionError, HTTPError, InvalidSchema, InvalidURL

from CommonServerUserPython import *

# disable insecure warnings
urllib3.disable_warnings()

INVALID_URL_ERROR = "Verify your server URL parameter that is correct and you have access to the server from your host"

COMPUTER_TABLE_HEADERS = ["ID", "hostName", "description", "groupID"]
COMPUTER_SETTINGS_TABLE_HEADERS = ["computerID", "name", "value"]
COMPUTER_GROUPS_TABLE_HEADERS = ["ID", "name", "description", "parentGroupID"]
FIREWALL_RULES_TABLE_HEADERS = ["ID", "name", "description", "direction", "action"]
POLICIES_TABLE_HEADERS = ["ID", "name", "description"]


class Client(BaseClient):
    """
    Client for TrendMicro RESTful API.

    Args:
        base_url (str): The base URL of TrendMicro.
        api_key (str): The API secret key for authenticating against Trend Micro.
        use_ssl (bool): Specifies whether to verify the SSL certificate or not.
        use_proxy (bool): Specifies if to use XSOAR proxy settings.
    """

    API_VERSION = "v1"
    _UPPER_CASE_WORDS = ["Tcp", "Ip", "Icmp", "Id"]

    def __init__(self, base_url: str, api_key: str, use_ssl: bool, use_proxy: bool):
        headers = {"api-secret-key": api_key, "api-version": self.API_VERSION}
        super().__init__(f"{base_url}/api", verify=use_ssl, proxy=use_proxy, headers=headers)

    def list_computers(self, expand: list[str], overrides: bool) -> list[dict[str, Any]]:
        """
        List all registered computers inside Trend Micro.

        Args:
            expand (List[str]): The desired information about the computers.
            overrides (bool): Whether to get the overridden properties or not.

        Returns:
            List[Dict[str, Any]]: The list of all computers.
        """

        params = {"expand": expand, "overrides": overrides}
        return self._http_request(method="GET", url_suffix="/computers", params=params).get("computers", [])

    def create_computer(self, expand: list, overrides: bool, **computer_properties) -> dict[str, Any]:
        """
        Create a new computer inside Trend Micro.

        Args:
            expand (List[str]): The desired information about the computers.
            overrides (bool): Whether to get the overridden properties or not.
            **computer_properties: The computer's properties.

        Returns:
            Dict[str, Any]: The new computer.
        """

        params = {"expand": expand, "overrides": overrides}
        return self._http_request(method="POST", url_suffix="/computers", params=params, json_data=computer_properties)

    def get_computer(self, computer_id: int, expand: list[str], overrides: bool) -> dict[str, Any]:
        """
        Get information about an existing computer inside Trend Micro.

        Args:
            computer_id (int): The computer id to obtain.
            expand (List[str]): The desired information about the computers.
            overrides (bool): Whether to get the overridden properties or not.

        Returns:
            Dict[str, Any]: The information of the computer.
        """

        params = {"expand": expand, "overrides": overrides}
        return self._http_request(method="GET", url_suffix=f"/computers/{computer_id}", params=params)

    def modify_computer(self, computer_id: int, expand: list[str], overrides: bool, **computer_properties) -> dict[str, Any]:
        """
        Modify properties of an existing computer inside Trend Micro.

        Args:
            computer_id (int): The computer id to obtain.
            expand (List[str]): The desired information about the computers.
            overrides (bool): Whether to get the overridden properties or not.
            **computer_properties: The computer properties to modify.

        Returns:
            Dict[str, Any]: The information about the modified computer.
        """

        params = {"expand": expand, "overrides": overrides}
        return self._http_request(
            method="POST", url_suffix=f"/computers/{computer_id}", params=params, json_data=computer_properties
        )

    def delete_computer(self, computer_id: int):
        """
        Delete an existing computer from Trend Micro.

        Args:
            computer_id (int): The computer id to obtain.
        """

        self._http_request(method="DELETE", url_suffix=f"/computers/{computer_id}", resp_type="response")

    def get_computer_setting(self, computer_id: int, setting_name: str, overrides: bool) -> dict[str, Any]:
        """
        Get information about a certain setting of an existing computer inside Trend Micro.

        Args:
            computer_id (int): The computer id to obtain.
            setting_name (str): The name of the computer's setting.
            overrides (bool): Whether to get the overridden properties or not.

        Returns:
            Dict[str, Any]: The information about computer's setting.
        """

        params = {"overrides": overrides}
        return self._http_request(method="GET", url_suffix=f"/computers/{computer_id}/settings/{setting_name}", params=params)

    def modify_computer_setting(self, computer_id: int, setting_name: str, overrides: bool, value: str) -> dict[str, Any]:
        """
        Modify the setting of an existing computer inside Trend Micro.

        Args:
            computer_id (int): The computer id to obtain.
            setting_name (str): The name of the computer's setting.
            overrides (bool): Whether to get the overridden properties or not.
            value (str): The value of the setting to modify.
        Returns:
            Dict[str, Any]: The information about computer's setting.
        """

        return self._http_request(
            method="POST",
            url_suffix=f"/computers/{computer_id}/settings/{setting_name}",
            params={"overrides": overrides},
            json_data={"value": value},
        )

    def reset_computer_setting(self, computer_id: int, setting_name: str, overrides: bool) -> dict[str, Any]:
        """
        Reset the setting of an existing computer inside Trend Micro.

        Args:
            computer_id (int): The computer id to obtain.
            setting_name (str): The name of the computer's setting.
            overrides (bool): Whether to get the overridden properties or not.
        Returns:
            Dict[str, Any]: The information about computer's setting.
        """

        return self._http_request(
            method="DELETE", url_suffix=f"/computers/{computer_id}/settings/{setting_name}", params={"overrides": overrides}
        )

    def list_firewall_rule_ids_of_computer(self, computer_id: int, overrides: bool) -> list[int]:
        """
        Get all rule IDs that are assigned to the computer.

        Args:
            computer_id (int): The ID of the computer get its rules.
            overrides (bool): Whether to get the rule IDs assigned directly to the current computer or not.

        Returns:
            List[int]: The rule IDs.
        """

        return self._http_request(
            method="GET", url_suffix=f"/computers/{computer_id}/firewall/assignments", params={"overrides": overrides}
        ).get("assignedRuleIDs", [])

    def add_firewall_rule_ids_to_computer(self, computer_id: int, rule_ids: list[int], overrides: bool) -> list[int]:
        """
        Assign more rule IDs to a certain computer.

        Args:
            computer_id (int): The computer ID to add the rules.
            rule_ids (List[int]): The IDs of the rules to assign to the computer.
            overrides (bool): Whether to get the rule IDs assigned directly to the current computer or not.

        Returns:
            List[int]: All rule IDs that are assigned to the computer.
        """

        return self._http_request(
            method="POST",
            url_suffix=f"/computers/{computer_id}/firewall/assignments",
            params={"overrides": overrides},
            json_data={"rule_ids": rule_ids},
        ).get("assignedRuleIDs", [])

    def set_firewall_rule_ids_to_computer(self, computer_id: int, rule_ids: list[int], overrides: bool) -> list[int]:
        """
        Assign the rule IDs to a certain computer.

        Args:
            computer_id (int): The computer ID to assign the rules.
            rule_ids (List[int]): The IDs of the rules to assign to the computer.
            overrides (bool): Whether to get the rule IDs assigned directly to the current computer or not.

        Returns:
            List[int]: All rule IDs that are assigned to the computer.
        """

        return self._http_request(
            method="PUT",
            url_suffix=f"/computers/{computer_id}/firewall/assignments",
            params={"overrides": overrides},
            json_data={"rule_ids": rule_ids},
        ).get("assignedRuleIDs", [])

    def remove_firewall_rule_id_from_computer(self, computer_id: int, firewall_rule_id: int):
        """
        Remove a firewall rule ID from a certain computer.

        Args:
            computer_id (int): The ID of the computer to remove the firewall rule.
            firewall_rule_id (int): The firewall rule ID to remove from the computer.
        """

        self._http_request(method="DELETE", url_suffix=f"/computers/{computer_id}/firewall/assignments/{firewall_rule_id}")

    def list_computer_groups(self) -> list[dict[str, Any]]:
        """
        List all computer groups inside Trend Micro.

        Returns:
            List[Dict[str, Any]]: All existing computer groups.
        """

        return self._http_request(method="GET", url_suffix="/computergroups").get("computerGroups", [])

    def create_computer_group(self, **computer_group_properties) -> dict[str, Any]:
        """
        Create a new computer group inside Trend Micro.

        Args:
            **computer_group_properties: The computer group's properties.

        Returns:
            Dict[str, Any]: The information of the computer group.
        """

        return self._http_request(method="POST", url_suffix="/computergroups", json_data=computer_group_properties)

    def get_computer_group(self, computer_group_id: int) -> dict[str, Any]:
        """
        Get information about a certain computer group.

        Args:
            computer_group_id (int): The ID of the computer group.

        Returns:
            Dict[str, Any]: The information of the computer group.
        """

        return self._http_request(method="GET", url_suffix=f"/computergroups/{computer_group_id}")

    def modify_computer_group(self, computer_group_id: int, **computer_group_properties) -> dict[str, Any]:
        """
        Modify a certain computer group properties.

        Args:
            computer_group_id (int): The ID of the computer group.
            **computer_group_properties: The computer group's properties to modify.

        Returns:
            Dict[str, Any]: The information about the computer group.
        """

        return self._http_request(
            method="POST", url_suffix=f"/computergroups/{computer_group_id}", json_data=computer_group_properties
        )

    def delete_computer_group(self, computer_group_id: int):
        """
        Delete a certain computer group from Trend Micro.

        Args:
            computer_group_id (int): The ID of the computer group to delete.
        """

        self._http_request(method="DELETE", url_suffix=f"/computergroups/{computer_group_id}", resp_type="response")

    def list_firewall_rules(self) -> list[dict[str, Any]]:
        """
        List all firewall rules inside Trend Micro.

        Returns:
            List[Dict[str, Any]]: All firewall rules.
        """

        return self._http_request(method="GET", url_suffix="/firewallrules").get("firewallRules", [])

    def create_firewall_rule(self, **firewall_rule_properties) -> dict[str, Any]:
        """
        Create a new firewall rule.

        Args:
            **firewall_rule_properties: The firewall rule properties.

        Returns:
            Dict[str, Any]: The new firewall rule.
        """

        return self._http_request(method="POST", url_suffix="/firewallrules", json_data=firewall_rule_properties)

    def get_firewall_rule(self, firewall_rule_id: int) -> dict[str, Any]:
        """
        Get information about a certain firewall rule.

        Args:
            firewall_rule_id (int): The ID of the firewall rule.

        Returns:
            Dict[str, Any]: The desired firewall rule.
        """

        return self._http_request(method="GET", url_suffix=f"/firewallrules/{firewall_rule_id}")

    def modify_firewall_rule(self, firewall_rule_id: int, **firewall_rule_properties) -> dict[str, Any]:
        """
        Modify a certain firewall rule properties.

        Args:
            firewall_rule_id (int): The ID of the firewall rule.
            **firewall_rule_properties: The firewall rule properties.

        Returns:
            Dict[str, Any]: The modified firewall rule.
        """

        return self._http_request(
            method="POST", url_suffix=f"/firewallrules/{firewall_rule_id}", json_data=firewall_rule_properties
        )

    def delete_firewall_rule(self, firewall_rule_id: int):
        """
        Delete a certain firewall rule from Trend Micro.

        Args:
            firewall_rule_id (int): The ID of the firewall rule to delete.
        """

        self._http_request(method="DELETE", url_suffix=f"/firewallrules/{firewall_rule_id}", resp_type="response")

    def search(
        self,
        resource: str,
        max_items: int,
        field_name: str,
        field_type: str,
        operation: str,
        value: str,
        sort_by_object_id: Optional[bool],
    ) -> list[dict[str, Any]]:
        """
        Search a resource, such as computers, by a query on a certain field.

        Args:
            resource (str): The name of the resource to search (computers, policies, firewallrules).
            max_items (int): The maximum number of items to get from the search request.
            field_name (str): The name of the field to query.
            field_type (str): The type of the field to query (string, integer, boolean).
            operation (str): The operation to test the field with the value.
            value (str): The value of the field to query.
            sort_by_object_id (bool): If true, forces the response objects to be sorted by ID.

        Returns:
            List[Dict[str, Any]]: The list of objects from type of the resource as a result of the query.
        """

        python_type_mapping = {"boolean": bool, "numeric": int, "string": str, "choice": str, "id": int, "version": str}
        value = convert_arg(value, python_type_mapping[field_type])

        search_criteria = [{"fieldName": field_name, f"{field_type}Test": operation, f"{field_type}Value": value}]
        body = {"max_items": max_items, "search_criteria": search_criteria, "sort_by_object_id": sort_by_object_id}

        return self._http_request(method="POST", url_suffix=f"/{resource.lower()}/search", json_data=body).get(resource, [])

    def get_policy(self, policy_id: int, overrides: bool) -> dict[str, Any]:
        """
        Get information about a certain policy.

        Args:
            policy_id (int): The ID of the policy to obtain its information.
            overrides (bool): Get only overrides defined for the current policy.

        Returns:
            Dict[str, Any]: The desired policy information.
        """

        return self._http_request(method="GET", url_suffix=f"/policies/{policy_id}", params={"overrides": overrides})

    def modify_policy(self, policy_id: int, overrides: bool, **policy_properties) -> dict[str, Any]:
        """
        Modify the properties of a certain policy.

        Args:
            policy_id (int): The policy ID to modify.
            overrides (bool): Get only overrides defined for the current policy.
            **policy_properties: The modified policy properties.

        Returns:
            Dict[str, Any]: The modified policy.
        """

        return self._http_request(
            method="POST", url_suffix=f"/policies/{policy_id}", params={"overrides": overrides}, json_data=policy_properties
        )

    def delete_policy(self, policy_id: int):
        """
        Delete a certain policy from Trend Micro.

        Args:
            policy_id (int): The policy ID to delete.
        """

        self._http_request(method="DELETE", url_suffix=f"/policies/{policy_id}", resp_type="response")

    def get_default_policy_setting(self, name: str) -> dict[str, Any]:
        """
        Get information about a certain default setting of Trend Micro's policies.

        Args:
            name (str): The name of the setting.

        Returns:
            Dict[str, Any]: The setting's value.
        """

        return self._http_request(method="GET", url_suffix=f"/policies/default/settings/{name}")

    def modify_default_policy_setting(self, name: str, value: str) -> dict[str, Any]:
        """
        Modify a certain default setting of Trend Micro's policies.

        Args:
            name (str): The name of the setting.
            value (str): The value to set to the setting.

        Returns:
            Dict[str, Any]: The new modified value.
        """

        return self._http_request(method="POST", url_suffix=f"/policies/default/settings/{name}", json_data={"value": value})

    def reset_default_policy_setting(self, name: str) -> dict[str, Any]:
        """
        Reset a certain default setting of Trend Micro's policies.

        Args:
            name (str): The name of the setting.

        Returns:
            Dict[str, Any]: The value of the setting after resetting it.
        """

        return self._http_request(method="DELETE", url_suffix=f"/policies/default/settings/{name}")

    def list_default_policy_settings(self) -> dict[str, dict[str, str]]:
        """
        Get all default settings of Trend Micro's settings.

        Returns:
            Dict[str, Dict[str, str]]: All default settings.
        """

        return self._http_request(method="GET", url_suffix="/policies/default")

    def get_policy_setting(self, policy_id: int, name: str, overrides: bool):
        """
        Get the information about a setting of a certain policy.

        Args:
            policy_id (int): The ID of the policy to get its setting.
            name (str) The name of the setting:
            overrides (bool): Get the value only if defined for the current policy.

        Returns:
            Dict[str, Any]: The setting information of the desired policy.
        """

        return self._http_request(
            method="GET", url_suffix=f"/policies/{policy_id}/settings/{name}", params={"overrides": overrides}
        )

    def modify_policy_setting(self, policy_id: int, name: str, overrides: bool, value: str) -> dict[str, Any]:
        """
        Modify the value of a setting of a certain policy.

        Args:
            policy_id (int): The ID of the policy to get its setting.
            name (str) The name of the setting:
            overrides (bool): Get the value only if defined for the current policy.
            value (str): The new value of the setting.

        Returns:
            Dict[str, Any]: The setting information of the desired policy.
        """

        return self._http_request(
            method="POST",
            url_suffix=f"/policies/{policy_id}/settings/{name}",
            params={"overrides": overrides},
            json_data={"value": value},
        )

    def reset_policy_setting(self, policy_id: int, name: str, overrides: bool) -> dict[str, Any]:
        """
        Reset the value of a setting of a certain policy.

        Args:
            policy_id (int): The ID of the policy to get its setting.
            name (str) The name of the setting:
            overrides (bool): Get the value only if defined for the current policy.

        Returns:
            Dict[str, Any]: The setting information of the desired policy after reset.
        """

        return self._http_request(
            method="DELETE", url_suffix=f"/policies/{policy_id}/settings/{name}", params={"overrides": overrides}
        )

    def list_policies(self, overrides: bool) -> list[dict[str, Any]]:
        """
        List all existing policies inside Trend Micro.

        Args:
            overrides (bool): Show only overrides defined for the current policy.

        Returns:
            List[Dict[str, Any]]: All policies.
        """

        return self._http_request(method="GET", url_suffix="/policies", params={"overrides": overrides}).get("policies", [])

    def create_policy(self, overrides: bool, **policy_properties) -> dict[str, Any]:
        """
        Create a new policy inside Trend Micro.

        Args:
            overrides (bool): Show only overrides defined for the current policy.
            **policy_properties: The new policy properties.

        Returns:
            Dict[str, Any]: The new policy.
        """

        return self._http_request(
            method="POST", url_suffix="/policies", params={"overrides": overrides}, json_data=policy_properties
        )

    def create_scheduled_task(self, name: str, _type: str, computer_id: int) -> dict:
        _type_to_parameter = {
            "scan-for-open-ports": "scanForOpenPortsTaskParameters",
            "scan-for-recommendations": "scanForRecommendationsTaskParameters",
            "scan-for-integrity-changes": "scanForIntegrityChangesTaskParameters",
            "scan-for-malware": "scanForMalwareTaskParameters",
        }

        body = {
            "name": name,
            "type": _type,
            "scheduleDetails": {"recurrenceType": "none", "onceOnlyScheduleParameters": {"startTime": 0}},
            "runNow": True,
            "enabled": True,
            _type_to_parameter[_type]: {"computerFilter": {"type": "computer", "computerID": computer_id}, "timeout": "never"},
        }

        return super()._http_request(method="POST", url_suffix="/scheduledtasks", json_data=body)

    def delete_scheduled_task(self, task_id: int):
        response = super()._http_request(method="DELETE", url_suffix=f"/scheduledtasks/{task_id}", resp_type="response")
        response.raise_for_status()
        return response

    def list_scheduled_tasks(self, task_id: Optional[int] = None) -> requests.Response:
        url_suffix = "/scheduledtasks"
        if task_id:
            url_suffix = f"{url_suffix}/{task_id}"
        return self._http_request(method="GET", url_suffix=url_suffix, resp_type="response", ok_codes=(200, 404))

    @no_type_check
    def _http_request(self, method: str, url_suffix: str = "", params: dict = None, json_data: dict = None, **kwargs):
        """
        Executing an HTTP request to Trend Micro.
        The function converts the name of the arguments to Trend Micro's convention (camelCase).

        Args:
            method (str): The method of the HTTP request.
            url_suffix (str): The endpoint to request.
            params (dict): The query parameters of the request.
            json_data (dict): The JSON body of the request.
            **kwargs: Additional arguments of the `Base Client`.
        Returns:
            The response in dict/list form / response object.
        """

        if params:
            params = {self._convert_convention(k): self._convert_value(v) for k, v in params.items() if v}
        if json_data:
            json_data = {self._convert_convention(k): self._convert_value(v) for k, v in json_data.items() if v}
        return super()._http_request(method, url_suffix, params=params, json_data=json_data, **kwargs)

    def _convert_convention(self, arg: str) -> str:
        """
        Converting an argument to Trend Micro API convention (camelCase except for the `_UPPER_CASE_WORDS`).

        Args:
            arg (str): The string to convert to the API convention.

        Returns:
            str: The string with the API convention.
        """

        camel_case_arg = camelize_string(arg, upper_camel=False)
        for word in self._UPPER_CASE_WORDS:
            camel_case_arg = camel_case_arg.replace(word, word.upper())

        return camel_case_arg

    @staticmethod
    def _convert_value(arg: Any) -> Any:
        if isinstance(arg, bool):
            return str(arg).lower()
        return arg


def convert_arg(value: Optional[str], type_hint: type) -> Any:
    """
    Converting a single argument from string into its real type.

    Args:
        value (str): The value of the argument to convert.
        type_hint (Type): The type of the argument to be converted to.

    Raises:
        ValueError: The argument cannot be converted.

    Returns:
        Any: The argument after conversion.
    """

    converters: dict[type, Callable] = {str: str, bool: argToBoolean, int: arg_to_number, list: argToList}

    origin_type_hint = get_origin(type_hint) or type_hint
    type_hint_args = get_args(type_hint)

    if origin_type_hint is Union and type(None) in type_hint_args:
        return convert_arg(value, type_hint_args[0]) if value else None
    try:
        return converters[origin_type_hint](value)
    except KeyError:
        raise ValueError(f"Failed to convert {value} to {origin_type_hint}")


def convert_args(command_function: Callable, args: dict[str, str]) -> dict[str, Any]:
    """
    Converting XSOAR string arguments into their real types (according to the requested command).

    Args:
        command_function (Callable): The function that handles the requested command.
        args (Dict[str, str]: XSOAR string arguments for the command.

    Returns:
        Dict[str, Any]: The arguments in their real types.
    """

    type_hints = get_type_hints(command_function)
    type_hints.pop("client", None)
    type_hints.pop("return", None)
    return {name: convert_arg(args.get(name), hint) for name, hint in type_hints.items()}


def list_computers_command(client: Client, expand: list[str], overrides: bool) -> CommandResults:
    """
    Get list of all computers from Trend Micro.

    Args:
        client (client): The Trend Micro API client.
        expand (List[str]): The desired information about the computers.
        overrides (bool): Whether to get the overridden properties or not.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.list_computers(expand=expand, overrides=overrides)
    markdown = tableToMarkdown(
        "All computers list", response, headerTransform=pascalToSpace, removeNull=True, headers=COMPUTER_TABLE_HEADERS
    )

    return CommandResults(
        outputs_prefix="TrendMicro.Computers",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def search_computers_command(
    client: Client,
    max_items: int,
    field_name: str,
    field_type: str,
    operation: str,
    value: str,
    sort_by_object_id: Optional[bool],
) -> CommandResults:
    """
    Search computers by a query on a certain field.

    Args:
        client (Client): The Trend Micro API client.
        max_items (int): The maximum number of items to get from the search request.
        field_name (str): The name of the field to query.
        field_type (str): The type of the field to query (string, integer, boolean).
        operation (str): The operation to test the field with the value.
        value (str): The value of the field to query.
        sort_by_object_id (Optional[bool]): If true, forces the response objects to be sorted by ID.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.search(
        "computers",
        max_items=max_items,
        field_name=field_name,
        field_type=field_type,
        operation=operation,
        value=value,
        sort_by_object_id=sort_by_object_id,
    )

    markdown = tableToMarkdown(
        "Matched Computers", response, removeNull=True, headers=COMPUTER_TABLE_HEADERS, headerTransform=pascalToSpace
    )

    return CommandResults(
        outputs_prefix="TrendMicro.Computers",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def create_computer_command(
    client: Client,
    expand: list[str],
    overrides: bool,
    host_name: str,
    display_name: Optional[str],
    description: Optional[str],
    group_id: Optional[int],
    policy_id: Optional[int],
    asset_importance_id: Optional[int],
    relay_list_id: Optional[int],
) -> CommandResults:
    """
    Create a new computer inside Trend Micro.

    Args:
        client (client): The Trend Micro API client.
        expand (List[str]): The desired information about the computers.
        overrides (bool): Whether to get the overridden properties or not.
        host_name (str): The hostname of the computer.
        display_name (Optional[str]): The display name of the computer.
        description (Optional[str]): The description about the new computer.
        group_id (Optional[int]): The computer group ID of the new computer.
        policy_id (Optional[int]): The ID of the desired policy to apply to new computer.
        asset_importance_id (Optional[int]): The asset importance ID to assign to the new computer.
        relay_list_id (Optional[int]): The ID of the relay list to assign to the new computer.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.create_computer(
        expand=expand,
        overrides=overrides,
        host_name=host_name,
        display_name=display_name,
        description=description,
        group_id=group_id,
        policy_id=policy_id,
        asset_importance_id=asset_importance_id,
        relay_list_id=relay_list_id,
    )

    markdown = tableToMarkdown(
        f"Details for the new computer {response.get('hostName', '')}",
        response,
        removeNull=True,
        headers=COMPUTER_TABLE_HEADERS,
        headerTransform=pascalToSpace,
    )

    return CommandResults(
        outputs_prefix="TrendMicro.Computers",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def get_computer_command(client: Client, computer_id: int, expand: list[str], overrides: bool) -> CommandResults:
    """
    Obtain information about an existing computer inside Trend Micro.

    Args:
        client (client): The Trend Micro API client.
        computer_id (int): The ID of the computer to get its information.
        expand (List[str]): The desired information about the computers.
        overrides (bool): Whether to get the overridden properties or not.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.get_computer(computer_id=computer_id, expand=expand, overrides=overrides)

    markdown = tableToMarkdown(
        f"Details for the computer {response.get('hostName', '')}",
        response,
        removeNull=True,
        headers=COMPUTER_TABLE_HEADERS,
        headerTransform=pascalToSpace,
    )

    return CommandResults(
        outputs_prefix="TrendMicro.Computers",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def modify_computer_command(
    client: Client,
    computer_id: int,
    expand: list[str],
    overrides: bool,
    host_name: Optional[str],
    display_name: Optional[str],
    description: Optional[str],
    group_id: Optional[int],
    policy_id: Optional[int],
    asset_importance_id: Optional[int],
    relay_list_id: Optional[int],
) -> CommandResults:
    """
    Modify an existing computer inside Trend Micro.

    Args:
        client (client): The Trend Micro API client.
        computer_id (int): The ID of the computer to modify.
        expand (List[str]): The desired information about the computers.
        overrides (bool): Whether to get the overridden properties or not.
        host_name (str): The hostname of the computer.
        display_name (Optional[str]): The display name of the computer.
        description (Optional[str]): The description about the new computer.
        group_id (Optional[int]): The computer group ID of the new computer.
        policy_id (Optional[int]): The ID of the desired policy to apply to new computer.
        asset_importance_id (Optional[int]): The asset importance ID to assign to the new computer.
        relay_list_id (Optional[int]): The ID of the relay list to assign to the new computer.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.modify_computer(
        computer_id=computer_id,
        expand=expand,
        overrides=overrides,
        host_name=host_name,
        display_name=display_name,
        description=description,
        group_id=group_id,
        policy_id=policy_id,
        asset_importance_id=asset_importance_id,
        relay_list_id=relay_list_id,
    )

    markdown = tableToMarkdown(
        f"Details for the computer {response.get('hostName', '')}",
        response,
        removeNull=True,
        headers=COMPUTER_TABLE_HEADERS,
        headerTransform=pascalToSpace,
    )

    return CommandResults(
        outputs_prefix="TrendMicro.Computers",
        outputs_key_field="TrendMicro",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def delete_computer_command(client: Client, computer_id: int) -> CommandResults:
    """
    Delete a computer from Trend Micro.

    Args:
        client (client): The Trend Micro API client.
        computer_id (int): The ID of the computer to delete.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    client.delete_computer(computer_id=computer_id)
    return CommandResults(readable_output="The computer was successfully deleted!")


def get_computer_setting_command(client: Client, computer_id: int, name: str, overrides: bool) -> CommandResults:
    """
    Get information of a certain computer setting from Trend Micro.

    Args:
        client (client): The Trend Micro API client.
        computer_id (int): The ID of the computer to delete.
        name (str): The name of the setting to get its value.
        overrides (bool): Whether to get the overridden properties or not.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.get_computer_setting(computer_id=computer_id, setting_name=name, overrides=overrides)
    response["computerId"] = computer_id
    response["name"] = name

    markdown = tableToMarkdown(
        f"Settings for computer {computer_id}", response, headers=COMPUTER_SETTINGS_TABLE_HEADERS, headerTransform=pascalToSpace
    )

    return CommandResults(
        outputs_prefix="TrendMicro.ComputersSettings",
        outputs_key_field=["computerId", "name"],
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def modify_computer_setting_command(client: Client, computer_id: int, name: str, overrides: bool, value: str) -> CommandResults:
    """
    Modify a certain setting of an existing computer inside Trend Micro.

    Args:
        client (client): The Trend Micro API client.
        computer_id (int): The ID of the computer to delete.
        name (str): The name of the setting to get its value.
        overrides (bool): Whether to get the overridden properties or not.
        value (str): The value to assign inside the computer setting.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.modify_computer_setting(computer_id=computer_id, setting_name=name, overrides=overrides, value=value)
    response["computerId"] = computer_id
    response["name"] = name

    markdown = tableToMarkdown(
        f"Settings for computer {computer_id}", response, headers=COMPUTER_SETTINGS_TABLE_HEADERS, headerTransform=pascalToSpace
    )

    return CommandResults(
        outputs_prefix="TrendMicro.ComputersSettings",
        outputs_key_field=["computerId", "name"],
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def reset_computer_setting_command(client: Client, computer_id: int, name: str, overrides: bool) -> CommandResults:
    """
    Reset a certain computer setting to its default value.

    Args:
        client (client): The Trend Micro API client.
        computer_id (int): The ID of the computer to delete.
        name (str): The name of the setting to get its value.
        overrides (bool): Whether to get the overridden properties or not.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.reset_computer_setting(computer_id=computer_id, setting_name=name, overrides=overrides)
    response["computerId"] = computer_id
    response["name"] = name

    markdown = tableToMarkdown(
        f"Settings for computer {computer_id}", response, headers=COMPUTER_SETTINGS_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.ComputersSettings",
        outputs_key_field=["computerId", "name"],
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def list_firewall_rule_ids_of_computer_command(client: Client, computer_id: int, overrides: bool) -> CommandResults:
    """
    Get all rule IDs that are assigned to the computer.

    Args:
        client (Client): The Trend Micro API client.
        computer_id (int): The ID of the computer get its rules.
        overrides (bool): Whether to get the rule IDs assigned directly to the current computer or not.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.list_firewall_rule_ids_of_computer(computer_id=computer_id, overrides=overrides)

    markdown = f"The firewall rules IDs that are assigned to {computer_id}: {', '.join(map(str, response))}"

    return CommandResults(
        outputs_prefix="TrendMicro.FirewallAssignments",
        outputs={"assignedRuleIDs": response},
        readable_output=markdown,
        raw_response=response,
    )


def add_firewall_rule_ids_to_computer_command(
    client: Client, computer_id: int, rule_ids: list[int], overrides: bool
) -> CommandResults:
    """
    Assign more rule IDs to a certain computer.

    Args:
        client (Client): The Trend Micro API client.
        computer_id (int): The computer ID to add the rules.
        rule_ids (List[int]): The IDs of the rules to assign to the computer.
        overrides (bool): Whether to get the rule IDs assigned directly to the current computer or not.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.add_firewall_rule_ids_to_computer(computer_id=computer_id, rule_ids=rule_ids, overrides=overrides)

    markdown = f"The firewall rules IDs that are assigned to computer {computer_id}: {', '.join(map(str, response))}"

    return CommandResults(
        outputs_prefix="TrendMicro.FirewallAssignments",
        outputs={"assignedRuleIDs": response},
        readable_output=markdown,
        raw_response=response,
    )


def set_firewall_rule_ids_to_computer_command(
    client: Client, computer_id: int, rule_ids: list[int], overrides: bool
) -> CommandResults:
    """
    Assign rule IDs to a certain computer.

    Args:
        client (Client): The Trend Micro API client.
        computer_id (int): The computer ID to assign the rules.
        rule_ids (List[int]): The IDs of the rules to assign to the computer.
        overrides (bool): Whether to get the rule IDs assigned directly to the current computer or not.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.set_firewall_rule_ids_to_computer(computer_id=computer_id, rule_ids=rule_ids, overrides=overrides)

    markdown = f"The firewall rules IDs that are assigned to computer {computer_id}: {', '.join(map(str, response))}"

    return CommandResults(
        outputs_prefix="TrendMicro.FirewallAssignments",
        outputs={"assignedRuleIDs": response},
        readable_output=markdown,
        raw_response=response,
    )


def remove_firewall_rule_id_from_computer_command(client: Client, computer_id: int, firewall_rule_id: int) -> CommandResults:
    """
    Remove a firewall rule ID from a certain computer.

    Args:
        client (Client): The Trend Micro API client.
        computer_id (int): The ID of the computer to remove the firewall rule.
        firewall_rule_id (int): The firewall rule ID to remove from the computer.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    client.remove_firewall_rule_id_from_computer(computer_id=computer_id, firewall_rule_id=firewall_rule_id)
    markdown = f"The firewall rule {firewall_rule_id} was successfully deleted from computer {computer_id}!"
    return CommandResults(readable_output=markdown)


def list_computer_groups_command(client: Client) -> CommandResults:
    """
    List all computer groups from Trend Micro.

    Args:
        client (Client): The Trend Micro API client.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.list_computer_groups()

    markdown = tableToMarkdown(
        "Computer Groups", response, removeNull=True, headers=COMPUTER_GROUPS_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.ComputerGroups",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def create_computer_group_command(client: Client, name: str, description: str, parent_group_id: int) -> CommandResults:
    """
    Create a new computer group inside Trend Micro.

    Args:
        client (Client): The Trend Micro API client.
        name (str): The name of the computer group.
        description (str): The description of the computer group.
        parent_group_id (int): The ID of the parent computer group.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.create_computer_group(name=name, description=description, parent_group_id=parent_group_id)

    markdown = tableToMarkdown(
        "Computer Groups", response, removeNull=True, headers=COMPUTER_GROUPS_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.ComputerGroups",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def search_computer_groups_command(
    client: Client,
    max_items: int,
    field_name: str,
    field_type: str,
    operation: str,
    value: str,
    sort_by_object_id: Optional[bool],
) -> CommandResults:
    """
    Search computer groups by a query on a certain field.

    Args:
        client (Client): The Trend Micro API client.
        max_items (int): The maximum number of items to get from the search request.
        field_name (str): The name of the field to query.
        field_type (str): The type of the field to query (string, integer, boolean).
        operation (str): The operation to test the field with the value.
        value (str): The value of the field to query.
        sort_by_object_id (Optional[bool]): If true, forces the response objects to be sorted by ID.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.search(
        "computerGroups",
        max_items=max_items,
        field_name=field_name,
        field_type=field_type,
        operation=operation,
        value=value,
        sort_by_object_id=sort_by_object_id,
    )

    markdown = tableToMarkdown(
        "Matched Computer Groups", response, removeNull=True, headers=COMPUTER_GROUPS_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.ComputerGroups",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def get_computer_group_command(client: Client, computer_group_id: int) -> CommandResults:
    """
    Get information about a certain computer group from Trend Micro.

    Args:
        client (Client): The Trend Micro API client.
        computer_group_id (int): The ID of the computer group to obtain its information.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.get_computer_group(computer_group_id=computer_group_id)

    markdown = tableToMarkdown(
        f"Computer Group {computer_group_id} Details",
        response,
        removeNull=True,
        headers=COMPUTER_GROUPS_TABLE_HEADERS,
        headerTransform=pascalToSpace,
    )
    return CommandResults(
        outputs_prefix="TrendMicro.ComputerGroups",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def modify_computer_group_command(
    client: Client, computer_group_id: int, name: Optional[str], description: Optional[str], parent_group_id: Optional[int]
) -> CommandResults:
    """
    Modify an existing computer group inside Trend Micro.

    Args:
        client (Client): The Trend Micro API client.
        computer_group_id (int): The ID of the computer group to modify.
        name (Optional[str]): The name of the computer group.
        description (Optional[str]): The description of the computer group.
        parent_group_id (Optional[str]): The ID of the parent group of the computer group.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.modify_computer_group(
        computer_group_id=computer_group_id, name=name, description=description, parent_group_id=parent_group_id
    )

    markdown = tableToMarkdown(
        "Computer Group", response, removeNull=True, headers=COMPUTER_GROUPS_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.ComputerGroups",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def delete_computer_group_command(client: Client, computer_group_id: int) -> CommandResults:
    """
    Delete an existing computer group from Trend Micro.

    Args:
        client (Client): The Trend Micro API client.
        computer_group_id (int): The ID of the computer group to delete.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    client.delete_computer_group(computer_group_id=computer_group_id)
    return CommandResults(readable_output="The computer group was successfully deleted!")


def search_firewall_rules_command(
    client: Client,
    max_items: int,
    field_name: str,
    field_type: str,
    operation: str,
    value: str,
    sort_by_object_id: Optional[bool],
) -> CommandResults:
    """
    Search firewall rules by a query on a certain field.

    Args:
        client (Client): The Trend Micro API client.
        max_items (int): The maximum number of items to get from the search request.
        field_name (str): The name of the field to query.
        field_type (str): The type of the field to query (string, integer, boolean).
        operation (str): The operation to test the field with the value.
        value (str): The value of the field to query.
        sort_by_object_id (Optional[bool]): If true, forces the response objects to be sorted by ID.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.search(
        "firewallRules",
        max_items=max_items,
        field_name=field_name,
        field_type=field_type,
        operation=operation,
        value=value,
        sort_by_object_id=sort_by_object_id,
    )

    markdown = tableToMarkdown(
        "Matched Firewall Rules", response, removeNull=True, headers=FIREWALL_RULES_TABLE_HEADERS, headerTransform=pascalToSpace
    )

    return CommandResults(
        outputs_prefix="TrendMicro.FirewallRules",
        outputs_key_field="id",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def list_firewall_rules_command(client: Client) -> CommandResults:
    """
    Get information about all existing firewall rules inside Trend Micro.

    Args:
        client (Client): The Trend Micro API client.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.list_firewall_rules()

    markdown = tableToMarkdown(
        "Firewall Rules", response, removeNull=True, headers=FIREWALL_RULES_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.FirewallRules",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def create_firewall_rule_command(
    client: Client,
    name: str,
    description: Optional[str],
    action: Optional[str],
    priority: Optional[str],
    direction: Optional[str],
    frame_type: Optional[str],
    frame_number: Optional[int],
    frame_not: Optional[bool],
    protocol: Optional[str],
    protocol_number: Optional[int],
    protocol_not: Optional[bool],
    source_ip_type: Optional[str],
    source_ip_value: Optional[str],
    source_ip_mask: Optional[str],
    source_ip_range_from: Optional[str],
    source_ip_range_to: Optional[str],
    source_ip_multiple: Optional[list[str]],
    source_ip_list_id: Optional[int],
    source_ip_not: Optional[bool],
    source_mac_type: Optional[str],
    source_mac_value: Optional[str],
    source_mac_multiple: Optional[list],
    source_mac_list_id: Optional[int],
    source_mac_not: Optional[bool],
    source_port_type: Optional[str],
    source_port_multiple: Optional[list[str]],
    source_port_list_id: Optional[int],
    source_port_not: Optional[bool],
    destination_ip_type: Optional[str],
    destination_ip_value: Optional[str],
    destination_ip_mask: Optional[str],
    destination_ip_range_from: Optional[str],
    destination_ip_range_to: Optional[str],
    destination_ip_multiple: Optional[list],
    destination_ip_list_id: Optional[int],
    destination_ip_not: Optional[bool],
    destination_mac_type: Optional[str],
    destination_mac_value: Optional[str],
    destination_mac_multiple: Optional[list[str]],
    destination_mac_list_id: Optional[int],
    destination_mac_not: Optional[bool],
    destination_port_type: Optional[str],
    destination_port_multiple: Optional[list[str]],
    destination_port_list_id: Optional[int],
    destination_port_not: Optional[bool],
    any_flags: Optional[bool],
    log_disabled: Optional[bool],
    include_packet_data: Optional[bool],
    alert_enabled: Optional[bool],
    schedule_id: Optional[int],
    context_id: Optional[int],
    tcp_flags: Optional[list[str]],
    tcp_not: Optional[bool],
    icmp_type: Optional[int],
    icmp_code: Optional[int],
    icmp_not: Optional[bool],
) -> CommandResults:
    """
    Args:
        client (Client): The Trend Micro API client.
        name (str): The name of the firewall rule.
        description (Optional[str]): The description of the firewall rule.
        action (Optional[str]): The action of the packet filter.
        priority (Optional[str]): The priority of the packet filter.
        direction (Optional[str]): The direction of the packet.
        frame_type (Optional[str]): The packet frame type.
        frame_number (Optional[int]): The Ethernet frame number
        frame_not (Optional[bool]): Controls if the frame setting should be inverted.
        protocol (Optional[str]): The protocol.
        protocol_number (Optional[int]): The protocol number.
        protocol_not (Optional[bool]): Controls if the protocol setting should be inverted.
        source_ip_type (Optional[str]): The source IP type.
        source_ip_value (Optional[str]): The source IP.
        source_ip_mask (Optional[str]): The source IP subnet mask.
        source_ip_range_from (Optional[str]): The first value for a range of source IP addresses.
        source_ip_range_to (Optional[str]): The last value for a range of source IP addresses.
        source_ip_multiple (Optional[List[str]]): List of source IP addresses.
        source_ip_list_id (Optional[int]): The ID of a certain source IP list.
        source_ip_not (Optional[bool]): Controls if the source IP setting should be inverted.
        source_mac_type (Optional[str]): The source MAC type.
        source_mac_value (Optional[str]): The source MAC.
        source_mac_multiple (Optional[List[str]]): List of MAC addresses.
        source_mac_list_id (Optional[int]): The ID of MAC address list.
        source_mac_not (Optional[bool]): Controls if the source MAC setting should be inverted.
        source_port_type (Optional[str]): The type of source port.
        source_port_multiple (Optional[List[str]]): List of source ports.
        source_port_list_id (Optional[int]): The ID of source port list.
        source_port_not (Optional[bool]): Controls if the source port setting should be inverted.
        destination_ip_type (Optional[str]): The destination IP type.
        destination_ip_value (Optional[str]): The destination IP.
        destination_ip_mask (Optional[str]): The destination IP mask.
        destination_ip_range_from (Optional[str]): The first value for a range of destination IP addresses.
        destination_ip_range_to (Optional[str]): The last value for a range of destination IP addresses.
        destination_ip_multiple (Optional[List[str]]): List of destination IP addresses.
        destination_ip_list_id (Optional[int]): The ID of destination IP list.
        destination_ip_not (Optional[bool]): Controls if the destination IP setting should be inverted.
        destination_mac_type (Optional[str]): The destination MAC type.
        destination_mac_value (Optional[str]): The destination MAC address.
        destination_mac_multiple (Optional[List[str]]): List of MAC addresses.
        destination_mac_list_id (Optional[int]): The ID of destination MAC list.
        destination_mac_not (Optional[bool]): Controls if the destination MAC setting should be inverted.
        destination_port_type (Optional[str]): The type of destination port.
        destination_port_multiple (Optional[List[str]]): List of destination ports.
        destination_port_list_id (Optional[int]): The ID of destination ports list.
        destination_port_not (Optional[bool]): Controls if the destination port setting should be inverted.
        any_flags (Optional[bool]): True if any flags are used.
        log_disabled (Optional[bool]): Controls if logging for this filter is disabled.
        include_packet_data (Optional[bool]): Controls if this filter should capture data for every log.
        alert_enabled (Optional[bool]): Controls if this filter should capture data for every log.
        schedule_id (Optional[int]): The ID of the schedule to control when this filter is "on".
        context_id (Optional[int]): The RuleContext that is applied to this filter.
        tcp_flags (Optional[List[str]]): The TCP flags to use.
        tcp_not (Optional[bool]): Controls if the TCP setting should be inverted.
        icmp_type (Optional[int]): The ICMP type.
        icmp_code (Optional[int]): The ICMP code.
        icmp_not (Optional[bool]): Controls if the ICMP setting should be inverted.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.create_firewall_rule(
        name=name,
        description=description,
        action=action,
        priority=priority,
        direction=direction,
        frame_type=frame_type,
        frame_number=frame_number,
        frame_not=frame_not,
        protocol=protocol,
        protocol_number=protocol_number,
        protocol_not=protocol_not,
        source_ip_type=source_ip_type,
        source_ip_value=source_ip_value,
        source_ip_mask=source_ip_mask,
        source_ip_range_from=source_ip_range_from,
        source_ip_range_to=source_ip_range_to,
        source_ip_multiple=source_ip_multiple,
        source_ip_list_id=source_ip_list_id,
        source_ip_not=source_ip_not,
        source_mac_type=source_mac_type,
        source_mac_value=source_mac_value,
        source_mac_multiple=source_mac_multiple,
        source_maclist_id=source_mac_list_id,
        source_mac_not=source_mac_not,
        source_port_type=source_port_type,
        source_port_multiple=source_port_multiple,
        source_port_list_id=source_port_list_id,
        source_port_not=source_port_not,
        destination_ip_type=destination_ip_type,
        destination_ip_value=destination_ip_value,
        destination_ip_mask=destination_ip_mask,
        destination_ip_range_from=destination_ip_range_from,
        destination_ip_range_to=destination_ip_range_to,
        destination_ip_multiple=destination_ip_multiple,
        destination_ip_list_id=destination_ip_list_id,
        destination_ip_not=destination_ip_not,
        destination_mac_type=destination_mac_type,
        destination_mac_value=destination_mac_value,
        destination_mac_multiple=destination_mac_multiple,
        destination_mac_list_id=destination_mac_list_id,
        destination_mac_not=destination_mac_not,
        destination_port_type=destination_port_type,
        destination_port_multiple=destination_port_multiple,
        destination_port_list_id=destination_port_list_id,
        destination_port_not=destination_port_not,
        any_flags=any_flags,
        log_disabled=log_disabled,
        include_packet_data=include_packet_data,
        alert_enabled=alert_enabled,
        schedule_id=schedule_id,
        context_id=context_id,
        tcp_flags=tcp_flags,
        tcp_not=tcp_not,
        icmp_type=icmp_type,
        icmp_code=icmp_code,
        icmp_not=icmp_not,
    )

    markdown = tableToMarkdown(
        "Firewall Rules", response, removeNull=True, headers=FIREWALL_RULES_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.FirewallRules",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def get_firewall_rule_command(client: Client, firewall_rule_id: int) -> CommandResults:
    """
    Get information about a certain firewall rule.

    Args:
        client (Client): The Trend Micro API client.
        firewall_rule_id (int): The firewall rule to get its information.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.get_firewall_rule(firewall_rule_id=firewall_rule_id)

    markdown = tableToMarkdown(
        f"Details of The Firewall Rule {firewall_rule_id}",
        response,
        removeNull=True,
        headers=FIREWALL_RULES_TABLE_HEADERS,
        headerTransform=pascalToSpace,
    )
    return CommandResults(
        outputs_prefix="TrendMicro.FirewallRules",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def modify_firewall_rule_command(
    client: Client,
    firewall_rule_id: int,
    name: Optional[str],
    description: Optional[str],
    action: Optional[str],
    priority: Optional[str],
    direction: Optional[str],
    frame_type: Optional[str],
    frame_number: Optional[int],
    frame_not: Optional[bool],
    protocol: Optional[str],
    protocol_number: Optional[int],
    protocol_not: Optional[bool],
    source_ip_type: Optional[str],
    source_ip_value: Optional[str],
    source_ip_mask: Optional[str],
    source_ip_range_from: Optional[str],
    source_ip_range_to: Optional[str],
    source_ip_multiple: Optional[list[str]],
    source_ip_list_id: Optional[int],
    source_ip_not: Optional[bool],
    source_mac_type: Optional[str],
    source_mac_value: Optional[str],
    source_mac_multiple: Optional[list],
    source_mac_list_id: Optional[int],
    source_mac_not: Optional[bool],
    source_port_type: Optional[str],
    source_port_multiple: Optional[list[str]],
    source_port_list_id: Optional[int],
    source_port_not: Optional[bool],
    destination_ip_type: Optional[str],
    destination_ip_value: Optional[str],
    destination_ip_mask: Optional[str],
    destination_ip_range_from: Optional[str],
    destination_ip_range_to: Optional[str],
    destination_ip_multiple: Optional[list],
    destination_ip_list_id: Optional[int],
    destination_ip_not: Optional[bool],
    destination_mac_type: Optional[str],
    destination_mac_value: Optional[str],
    destination_mac_multiple: Optional[list[str]],
    destination_mac_list_id: Optional[int],
    destination_mac_not: Optional[bool],
    destination_port_type: Optional[str],
    destination_port_multiple: Optional[list[str]],
    destination_port_list_id: Optional[int],
    destination_port_not: Optional[bool],
    any_flags: Optional[bool],
    log_disabled: Optional[bool],
    include_packet_data: Optional[bool],
    alert_enabled: Optional[bool],
    schedule_id: Optional[int],
    context_id: Optional[int],
    tcp_flags: Optional[list[str]],
    tcp_not: Optional[bool],
    icmp_type: Optional[int],
    icmp_code: Optional[int],
    icmp_not: Optional[bool],
) -> CommandResults:
    """
    Modify a certain firewall rule.

    Args:
        client (Client): The Trend Micro API client.
        firewall_rule_id (int): The ID of the firewall rule to modify.
        name (Optional[str]): The name of the firewall rule.
        description (Optional[str]): The description of the firewall rule.
        action (Optional[str]): The action of the packet filter.
        priority (Optional[str]): The priority of the packet filter.
        direction (Optional[str]): The direction of the packet.
        frame_type (Optional[str]): The packet frame type.
        frame_number (Optional[int]): The Ethernet frame number
        frame_not (Optional[bool]): Controls if the frame setting should be inverted.
        protocol (Optional[str]): The protocol.
        protocol_number (Optional[int]): The protocol number.
        protocol_not (Optional[bool]): Controls if the protocol setting should be inverted.
        source_ip_type (Optional[str]): The source IP type.
        source_ip_value (Optional[str]): The source IP.
        source_ip_mask (Optional[str]): The source IP subnet mask.
        source_ip_range_from (Optional[str]): The first value for a range of source IP addresses.
        source_ip_range_to (Optional[str]): The last value for a range of source IP addresses.
        source_ip_multiple (Optional[List[str]]): List of source IP addresses.
        source_ip_list_id (Optional[int]): The ID of a certain source IP list.
        source_ip_not (Optional[bool]): Controls if the source IP setting should be inverted.
        source_mac_type (Optional[str]): The source MAC type.
        source_mac_value (Optional[str]): The source MAC.
        source_mac_multiple (Optional[List[str]]): List of MAC addresses.
        source_mac_list_id (Optional[int]): The ID of MAC address list.
        source_mac_not (Optional[bool]): Controls if the source MAC setting should be inverted.
        source_port_type (Optional[str]): The type of source port.
        source_port_multiple (Optional[List[str]]): List of source ports.
        source_port_list_id (Optional[int]): The ID of source port list.
        source_port_not (Optional[bool]): Controls if the source port setting should be inverted.
        destination_ip_type (Optional[str]): The destination IP type.
        destination_ip_value (Optional[str]): The destination IP.
        destination_ip_mask (Optional[str]): The destination IP mask.
        destination_ip_range_from (Optional[str]): The first value for a range of destination IP addresses.
        destination_ip_range_to (Optional[str]): The last value for a range of destination IP addresses.
        destination_ip_multiple (Optional[List[str]]): List of destination IP addresses.
        destination_ip_list_id (Optional[int]): The ID of destination IP list.
        destination_ip_not (Optional[bool]): Controls if the destination IP setting should be inverted.
        destination_mac_type (Optional[str]): The destination MAC type.
        destination_mac_value (Optional[str]): The destination MAC address.
        destination_mac_multiple (Optional[List[str]]): List of MAC addresses.
        destination_mac_list_id (Optional[int]): The ID of destination MAC list.
        destination_mac_not (Optional[bool]): Controls if the destination MAC setting should be inverted.
        destination_port_type (Optional[str]): The type of destination port.
        destination_port_multiple (Optional[List[str]]): List of destination ports.
        destination_port_list_id (Optional[int]): The ID of destination ports list.
        destination_port_not (Optional[bool]): Controls if the destination port setting should be inverted.
        any_flags (Optional[bool]): True if any flags are used.
        log_disabled (Optional[bool]): Controls if logging for this filter is disabled.
        include_packet_data (Optional[bool]): Controls if this filter should capture data for every log.
        alert_enabled (Optional[bool]): Controls if this filter should capture data for every log.
        schedule_id (Optional[int]): The ID of the schedule to control when this filter is "on".
        context_id (Optional[int]): The RuleContext that is applied to this filter.
        tcp_flags (Optional[List[str]]): The TCP flags to use.
        tcp_not (Optional[bool]): Controls if the TCP setting should be inverted.
        icmp_type (Optional[int]): The ICMP type.
        icmp_code (Optional[int]): The ICMP code.
        icmp_not (Optional[bool]): Controls if the ICMP setting should be inverted.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.modify_firewall_rule(
        firewall_rule_id,
        name=name,
        description=description,
        action=action,
        priority=priority,
        direction=direction,
        frame_type=frame_type,
        frame_number=frame_number,
        frame_not=frame_not,
        protocol=protocol,
        protocol_number=protocol_number,
        protocol_not=protocol_not,
        source_ip_type=source_ip_type,
        source_ip_value=source_ip_value,
        source_ip_mask=source_ip_mask,
        source_ip_range_from=source_ip_range_from,
        source_ip_range_to=source_ip_range_to,
        source_ip_multiple=source_ip_multiple,
        source_ip_list_id=source_ip_list_id,
        source_ip_not=source_ip_not,
        source_mac_type=source_mac_type,
        source_mac_value=source_mac_value,
        source_mac_multiple=source_mac_multiple,
        source_maclist_id=source_mac_list_id,
        source_mac_not=source_mac_not,
        source_port_type=source_port_type,
        source_port_multiple=source_port_multiple,
        source_port_list_id=source_port_list_id,
        source_port_not=source_port_not,
        destination_ip_type=destination_ip_type,
        destination_ip_value=destination_ip_value,
        destination_ip_mask=destination_ip_mask,
        destination_ip_range_from=destination_ip_range_from,
        destination_ip_range_to=destination_ip_range_to,
        destination_ip_multiple=destination_ip_multiple,
        destination_ip_list_id=destination_ip_list_id,
        destination_ip_not=destination_ip_not,
        destination_mac_type=destination_mac_type,
        destination_mac_value=destination_mac_value,
        destination_mac_multiple=destination_mac_multiple,
        destination_mac_list_id=destination_mac_list_id,
        destination_mac_not=destination_mac_not,
        destination_port_type=destination_port_type,
        destination_port_multiple=destination_port_multiple,
        destination_port_list_id=destination_port_list_id,
        destination_port_not=destination_port_not,
        any_flags=any_flags,
        log_disabled=log_disabled,
        include_packet_data=include_packet_data,
        alert_enabled=alert_enabled,
        schedule_id=schedule_id,
        context_id=context_id,
        tcp_flags=tcp_flags,
        tcp_not=tcp_not,
        icmp_type=icmp_type,
        icmp_code=icmp_code,
        icmp_not=icmp_not,
    )

    markdown = tableToMarkdown(
        f"Details About The Modified Firewall Rule {firewall_rule_id}",
        response,
        removeNull=True,
        headers=FIREWALL_RULES_TABLE_HEADERS,
        headerTransform=pascalToSpace,
    )
    return CommandResults(
        outputs_prefix="TrendMicro.FirewallRules",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def delete_firewall_rule_command(client: Client, firewall_rule_id: int) -> CommandResults:
    """
    Delete a certain firewall rule from Trend Micro.

    Args:
        client (Client): The Trend Micro API client.
        firewall_rule_id (int): The ID of the firewall rule to delete.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    client.delete_firewall_rule(firewall_rule_id=firewall_rule_id)
    return CommandResults(readable_output="The firewall rule was successfully deleted!")


def search_policies_command(
    client: Client,
    max_items: int,
    field_name: str,
    field_type: str,
    operation: str,
    value: str,
    sort_by_object_id: Optional[bool],
) -> CommandResults:
    """
    Search firewall rules by a query on a certain field.

    Args:
        client (Client): The Trend Micro API client.
        max_items (int): The maximum number of items to get from the search request.
        field_name (str): The name of the field to query.
        field_type (str): The type of the field to query (string, integer, boolean).
        operation (str): The operation to test the field with the value.
        value (str): The value of the field to query.
        sort_by_object_id (Optional[bool]): If true, forces the response objects to be sorted by ID.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.search(
        "policies",
        max_items=max_items,
        field_name=field_name,
        field_type=field_type,
        operation=operation,
        value=value,
        sort_by_object_id=sort_by_object_id,
    )

    markdown = tableToMarkdown(
        "Matched Policies", response, removeNull=True, headers=POLICIES_TABLE_HEADERS, headerTransform=pascalToSpace
    )

    return CommandResults(
        outputs_prefix="TrendMicro.Policies",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def get_policy_command(client: Client, policy_id: int, overrides: bool) -> CommandResults:
    """
    Get information about a certain policy.

    Args:
        client (Client): The Trend Micro API client.
        policy_id (int): The ID of the policy to get its information.
        overrides (bool): Show only overrides defined for the current policy.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.get_policy(policy_id=policy_id, overrides=overrides)

    markdown = tableToMarkdown(
        f"Details About The Policy {policy_id}",
        response,
        removeNull=True,
        headers=POLICIES_TABLE_HEADERS,
        headerTransform=pascalToSpace,
    )
    return CommandResults(
        outputs_prefix="TrendMicro.Policies",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def modify_policy_command(
    client: Client,
    policy_id: int,
    overrides: bool,
    name: Optional[str],
    parent_id: Optional[int],
    description: Optional[str],
    recommendation_scan_mode: Optional[str],
    auto_requires_update: Optional[str],
) -> CommandResults:
    """
    Modify a certain policy.

    Args:
        client (Client): The Trend Micro API client.
        policy_id (int): The ID of the policy to modify.
        overrides (bool): Show only overrides defined for the current policy.
        name (Optional[str]): The name of the policy.
        parent_id (Optional[int]): The ID of the parent policy.
        description (Optional[str]): The description of the policy.
        recommendation_scan_mode (Optional[str]): Enable recommendation scans for computers assigned this policy.
        auto_requires_update (Optional[str]): Update computers assigned this policy when the configuration changes.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.modify_policy(
        policy_id=policy_id,
        overrides=overrides,
        parent_id=parent_id,
        name=name,
        description=description,
        recommendation_scan_mode=recommendation_scan_mode,
        auto_requires_update=auto_requires_update,
    )

    markdown = tableToMarkdown(
        "Details About The Modified Policy",
        response,
        removeNull=True,
        headers=POLICIES_TABLE_HEADERS,
        headerTransform=pascalToSpace,
    )
    return CommandResults(
        outputs_prefix="TrendMicro.Policies",
        outputs_key_field="ID",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def delete_policy_command(client: Client, policy_id: int) -> CommandResults:
    """
    Delete a certain policy.

    Args:
        client (Client): The Trend Micro API client.
        policy_id (int): The ID of the policy to delete.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    client.delete_policy(policy_id=policy_id)
    return CommandResults(readable_output="The policy was successfully deleted!")


def get_default_policy_setting_command(client: Client, name: str) -> CommandResults:
    """
    Get information about a certain default policy setting.

    Args:
        client (Client): The Trend Micro API client.
        name (str): The name of the default policy setting.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.get_default_policy_setting(name=name)
    response["name"] = name

    markdown = tableToMarkdown(
        "Default Policy Setting", response, removeNull=True, headers=["name", "value"], headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.DefaultPolicySettings",
        outputs_key_field="name",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def modify_default_policy_setting_command(client: Client, name: str, value: str) -> CommandResults:
    """
    Modify a certain default policy setting.

    Args:
        client (Client): The Trend Micro API client.
        name (str): The name of the default policy setting.
        value (str): The new value to set to the setting.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.modify_default_policy_setting(name=name, value=value)
    response["name"] = name

    markdown = tableToMarkdown(
        "Default Policy Setting", response, removeNull=True, headers=["name", "value"], headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.DefaultPolicySettings",
        outputs_key_field="name",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def reset_default_policy_setting_command(client: Client, name: str) -> CommandResults:
    """
    Reset a certain default policy setting.

    Args:
        client (Client): The Trend Micro API client.
        name (str): The name of the default policy setting.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.reset_default_policy_setting(name=name)
    response["name"] = name

    markdown = tableToMarkdown(
        "Default Policy Setting", response, removeNull=True, headers=["name", "value"], headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.DefaultPolicySettings",
        outputs_key_field="name",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def list_default_policy_settings_command(client: Client) -> CommandResults:
    """
    Reset a certain default policy setting.

    Args:
        client (Client): The Trend Micro API client.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = {k: v.get("value") for k, v in client.list_default_policy_settings().items()}
    markdown = tableToMarkdown("The Default Policy Settings", response, removeNull=True, headerTransform=pascalToSpace)
    outputs = [{"name": k, "value": v} for k, v in response.items()]

    return CommandResults(
        outputs_prefix="TrendMicro.DefaultPolicySettings",
        outputs_key_field="name",
        outputs=outputs,
        readable_output=markdown,
        raw_response=response,
    )


def get_policy_setting_command(client: Client, policy_id: int, name: str, overrides: bool) -> CommandResults:
    """
    Get information about a setting of a certain policy.

    Args:
        client (Client): The Trend Micro API client.
        policy_id (int): The ID of the policy to get information about one of its settings.
        name (str): The name of the setting to obtain.
        overrides (bool): Show the value only if defined for the current policy.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.get_policy_setting(policy_id=policy_id, name=name, overrides=overrides)
    response["policyId"] = policy_id
    response["name"] = name

    markdown = tableToMarkdown(
        "The Policy Setting", response, removeNull=True, headers=["policyId", "name", "value"], headerTransform=pascalToSpace
    )

    return CommandResults(
        outputs_prefix="TrendMicro.PolicySettings",
        outputs_key_field="policyId",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def modify_policy_setting_command(client: Client, policy_id: int, name: str, overrides: bool, value: str) -> CommandResults:
    """
    Modify a setting of a certain policy.

    Args:
        client (Client): The Trend Micro API client.
        policy_id (int): The ID of the policy to modify one of its settings.
        name (str): The name of the setting to modify.
        overrides (bool): Show the value only if defined for the current policy.
        value (str): The value to set to the setting.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.modify_policy_setting(policy_id=policy_id, name=name, overrides=overrides, value=value)
    response["policyId"] = policy_id
    response["name"] = name

    markdown = tableToMarkdown(
        "The Policy Setting: ", response, removeNull=True, headers=["policyId", "name", "value"], headerTransform=pascalToSpace
    )

    return CommandResults(
        outputs_prefix="TrendMicro.PolicySettings",
        outputs_key_field="policyId",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def reset_policy_setting_command(client: Client, policy_id: int, name: str, overrides: bool) -> CommandResults:
    """
    Reset the value of a setting of a certain policy.

    Args:
        client (Client): The Trend Micro API client.
        policy_id (int): The ID of the policy to reset one of its settings.
        name (str): The name of the setting to reset.
        overrides (bool): Show the value only if defined for the current policy.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.reset_policy_setting(policy_id=policy_id, name=name, overrides=overrides)
    response["policyId"] = policy_id
    response["name"] = name

    markdown = tableToMarkdown(
        "The Policy Setting", response, removeNull=True, headerTransform=pascalToSpace, headers=["policyId", "name", "value"]
    )

    return CommandResults(
        outputs_prefix="TrendMicro.PolicySettings",
        outputs_key_field="policyId",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def list_policies_command(client: Client, overrides: bool) -> CommandResults:
    """
    Get information about all existing policies.

    Args:
        client (Client): The Trend Micro API client.
        overrides (bool): Show only overrides defined for the current policy.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.list_policies(overrides=overrides)

    markdown = tableToMarkdown(
        "Policies list", response, removeNull=True, headers=POLICIES_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.Policies",
        outputs_key_field="id",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def create_policy_command(
    client: Client,
    name: str,
    overrides: bool,
    parent_id: Optional[int],
    description: Optional[str],
    recommendation_scan_mode: Optional[str],
    auto_requires_update: Optional[str],
) -> CommandResults:
    """
    Create a new policy.

    Args:
        client (Client): The Trend Micro API client.
        name (str): The name of the policy.
        overrides (bool): Show only overrides defined for the current policy.
        parent_id (Optional[int]): The ID of the parent policy.
        description (Optional[str]): The description of the policy.
        recommendation_scan_mode (Optional[str]): Enable recommendation scans for computers assigned this policy.
        auto_requires_update (Optional[str]): Update computers assigned this policy when the configuration changes.

    Returns:
        CommandResults: Command results with raw response, outputs and readable outputs.
    """

    response = client.create_policy(
        overrides=overrides,
        parent_id=parent_id,
        name=name,
        description=description,
        recommendation_scan_mode=recommendation_scan_mode,
        auto_requires_update=auto_requires_update,
    )

    markdown = tableToMarkdown(
        "The New Policy", response, removeNull=True, headers=POLICIES_TABLE_HEADERS, headerTransform=pascalToSpace
    )
    return CommandResults(
        outputs_prefix="TrendMicro.Policies",
        outputs_key_field="id",
        outputs=response,
        readable_output=markdown,
        raw_response=response,
    )


def create_once_only_scan_scheduled_task_command(client: Client, name: str, type: str, computer_id: int):
    """
    Creates a scan scheduled task on a computer ID.

    Args:
         name (str): the name of the task
         type (str): the type of the scheduled task
         computer_id (int): the computer ID to run the scheduled task on
    """
    response = client.create_scheduled_task(name, _type=type, computer_id=computer_id)
    return CommandResults(
        outputs_prefix="TrendMicro.ScheduledTask",
        outputs_key_field="ID",
        raw_response=response,
        outputs=response,
        readable_output=f"Once-only scheduled task, named {name} for the "
        f"computer ID {computer_id} has been successfully created and run.",
    )


def delete_scheduled_task_command(client: Client, task_ids: List[int]):
    """
    Deletes a scheduled task(s)

    Args:
        task_ids int: task ID to delete
    """
    results = []

    for task_id in task_ids:
        try:
            _task_id = arg_to_number(task_id)
            if not _task_id:
                raise ValueError(f"Could not parse {_task_id} into integer")
        except ValueError:
            results.append(
                CommandResults(
                    entry_type=EntryType.ERROR, readable_output=f"task-ID {task_id} provided is invalid, must be integer"
                )
            )
        else:
            try:
                client.delete_scheduled_task(_task_id)
                results.append(CommandResults(readable_output=f"Scheduled task with ID {task_id} has been successfully deleted."))
            except Exception as error:
                demisto.error(f"Failed to delete task-ID {task_id}, {error=}")
                results.append(CommandResults(entry_type=EntryType.ERROR, readable_output=f"Failed to delete {task_id}"))

    return results


def list_scheduled_task_command(client: Client, task_id: Optional[int]):
    """
    Lists all the available scheduled tasks

    Args:
        task_id (int): querying for a specific scheduled task-ID.
    """
    response = client.list_scheduled_tasks(task_id)
    if response.status_code == 404:
        return CommandResults(readable_output=f"Could not find scheduled task with ID {task_id}")

    raw_response = response.json()
    context_output = raw_response.get("scheduledTasks") or raw_response

    if isinstance(context_output, dict):
        context_output = [context_output]

    if context_output:
        return CommandResults(
            outputs=context_output,
            raw_response=raw_response,
            outputs_prefix="TrendMicro.ScheduledTask",
            outputs_key_field="ID",
            readable_output=tableToMarkdown(
                "Scheduled Tasks",
                context_output,
                headers=["ID", "name", "type", "enabled", "lastRunTime"],
                headerTransform=pascalToSpace,
                date_fields=["lastRunTime", "nextRunTime"],
                removeNull=True,
            ),
        )

    return CommandResults(readable_output="There are no existing scheduled tasks.")


def test_module(client: Client, **_) -> str:
    """
    Testing the Trend Micro API.

    Args:
        client (Client): The Trend Micro API Client

    Returns:
        str: The result of the testing (*ok* for success, anything else for failure).
    """

    try:
        client.list_computers(expand=["none"], overrides=False)
        return "ok"
    except Exception as e:
        return str(e)


def main():
    params = demisto.params()

    use_ssl = not params.get("insecure", False)
    use_proxy = params.get("proxy", False)
    api_secret = params.get("credentials_api_secret", {}).get("password") or params.get("api_secret")
    if not api_secret:
        return_error("API secret must be provided.")
    client = Client(params.get("server_url"), api_secret, use_ssl, use_proxy)

    commands: dict[str, Callable] = {
        "trendmicro-list-computers": list_computers_command,
        "trendmicro-create-computer": create_computer_command,
        "trendmicro-search-computers": search_computers_command,
        "trendmicro-get-computer": get_computer_command,
        "trendmicro-modify-computer": modify_computer_command,
        "trendmicro-delete-computer": delete_computer_command,
        "trendmicro-get-computer-setting": get_computer_setting_command,
        "trendmicro-modify-computer-setting": modify_computer_setting_command,
        "trendmicro-reset-computer-setting": reset_computer_setting_command,
        "trendmicro-list-firewall-rule-ids-of-computer": list_firewall_rule_ids_of_computer_command,
        "trendmicro-add-firewall-rule-ids-to-computer": add_firewall_rule_ids_to_computer_command,
        "trendmicro-set-firewall-rule-ids-to-computer": set_firewall_rule_ids_to_computer_command,
        "trendmicro-remove-firewall-rule-id-from-computer": remove_firewall_rule_id_from_computer_command,  # noqa: E501
        "trendmicro-list-computer-groups": list_computer_groups_command,
        "trendmicro-create-computer-group": create_computer_group_command,
        "trendmicro-search-computer-groups": search_computer_groups_command,
        "trendmicro-get-computer-group": get_computer_group_command,
        "trendmicro-modify-computer-group": modify_computer_group_command,
        "trendmicro-delete-computer-group": delete_computer_group_command,
        "trendmicro-search-firewall-rules": search_firewall_rules_command,
        "trendmicro-list-firewall-rules": list_firewall_rules_command,
        "trendmicro-create-firewall-rule": create_firewall_rule_command,
        "trendmicro-get-firewall-rule": get_firewall_rule_command,
        "trendmicro-modify-firewall-rule": modify_firewall_rule_command,
        "trendmicro-delete-firewall-rule": delete_firewall_rule_command,
        "trendmicro-search-policies": search_policies_command,
        "trendmicro-get-policy": get_policy_command,
        "trendmicro-modify-policy": modify_policy_command,
        "trendmicro-delete-policy": delete_policy_command,
        "trendmicro-get-default-policy-setting": get_default_policy_setting_command,
        "trendmicro-modify-default-policy-setting": modify_default_policy_setting_command,
        "trendmicro-reset-default-policy-setting": reset_default_policy_setting_command,
        "trendmicro-list-default-policy-settings": list_default_policy_settings_command,
        "trendmicro-get-policy-setting": get_policy_setting_command,
        "trendmicro-modify-policy-setting": modify_policy_setting_command,
        "trendmicro-reset-policy-setting": reset_policy_setting_command,
        "trendmicro-list-policies": list_policies_command,
        "trendmicro-create-policy": create_policy_command,
        "trendmicro-create-onceonly-scan-scheduled-task": create_once_only_scan_scheduled_task_command,  # noqa: E501
        "trendmicro-delete-scheduled-task": delete_scheduled_task_command,
        "trendmicro-list-scheduled-task": list_scheduled_task_command,
        "test-module": test_module,
    }

    try:
        command = demisto.command()

        command_function = commands.get(command)
        if not command_function:
            raise NotImplementedError(f"The command {command} does not exist on TrendMicro!")
        else:
            return_results(command_function(client, **convert_args(command_function, demisto.args())))
    except (ConnectionError, InvalidURL, InvalidSchema) as e:
        error_message = f"{INVALID_URL_ERROR}\nError:\n{e}"
        return_error(error_message)
    except HTTPError as e:
        error_message = f"Error in API call [{e.response.status_code}]\n{e.response.json().get('message')}"
        return_error(error_message)
    except Exception as e:
        error_message = f"Failed to execute {demisto.command()} command.\nError:\n{e}"
        return_error(error_message)


if __name__ in ("__main__", "__builtin__", "builtins"):
    main()
