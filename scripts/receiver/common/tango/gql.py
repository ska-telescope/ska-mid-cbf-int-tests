"""TangoGQL-based client."""

from typing import Any, List, Optional

from ..graphql import GraphQLClient
from .base import TangoClient


class DevError(Exception):
    """
    Tango device error exception.

    :param desc: description of exception
    :param reason: reason for exception
    """

    def __init__(self, desc=None, reason=None):
        super().__init__()
        self.desc = desc
        self.reason = reason


class TangoClientGQL(TangoClient):
    """
    Client for a Tango device using TangoGQL.

    :param url: URL of TangoGQL server
    :param device: name of device
    :param translations: optional translations for attribute values
    """

    query_get_commands = """
        query GetCommands($device: String!) {
            device(name: $device) {
                commands {
                    name
                }
            }
        }
    """

    query_fetch_attribute_names = """
        query FetchAttributeNames($device: String!) {
          device(name: $device) {
            attributes {
              name
              label
              dataformat
              datatype
            }
          }
        }
    """

    query_get_attribute = """
        query GetAttribute($device: String!, $attribute: String!) {
            device(name: $device) {
                attributes(pattern: $attribute) {
                    value
                }
            }
        }
    """

    mutation_execute_command = """
        mutation ExecuteCommand($device: String!, $command: String!, $argument: ScalarTypes) {
            executeCommand(device: $device, command: $command, argin: $argument) {
                ok
                message
                output
            }
        }
    """  # noqa: E501

    def __init__(
        self, url: str, device: str, translations: Optional[dict] = None
    ):
        super().__init__(device, translations=translations)
        self._client = GraphQLClient(f"{url}/db")

    def get_commands(self) -> Optional[List[str]]:
        """
        Get list of commands from device.

        :returns: list of command names

        """
        variables = {"device": self._device}
        response = self._client.execute(self.query_get_commands, variables)
        commands = [
            command["name"]
            for command in response["data"]["device"]["commands"]
        ]
        if not commands:
            self._exception = DevError(
                desc=f"Device {self._device} is not exported",
                reason="API_DeviceNotExported",
            )
        return commands

    def fetch_attribute_names(self) -> Optional[List[str]]:
        """
        Get list of attributes from device.

        :returns: list of attribute names

        """
        variables = {"device": self._device}
        response = self._client.execute(
            self.query_fetch_attribute_names, variables
        )
        attributes = [
            attribute["name"]
            for attribute in response["data"]["device"]["attributes"]
        ]
        if not attributes:
            self._exception = DevError(
                desc=f"Device {self._device} is not exported",
                reason="API_DeviceNotExported",
            )
        return attributes

    def get_attribute(self, attribute: str) -> Any:
        """
        Get value of device attribute.

        :param attribute: name of attribute
        :returns: value of attribute

        """
        variables = {"device": self._device, "attribute": attribute}
        response = self._client.execute(self.query_get_attribute, variables)
        attributes = response["data"]["device"]["attributes"]
        if attributes:
            value = attributes[0]["value"]
            if self._translations and attribute in self._translations:
                value = self._translations[attribute][value]
        else:
            value = None
            self._exception = DevError(
                desc=f"Device {self._device} is not exported",
                reason="API_DeviceNotExported",
            )
        return value

    def execute_command(
        self, command: str, argument: Optional[str] = None
    ) -> Any:
        """
        Execute command.

        :param command: name of command
        :param argument: optional argument for command
        :returns: return value of command

        """
        variables = {
            "device": self._device,
            "command": command,
            "argument": argument,
        }
        response = self._client.execute(
            self.mutation_execute_command, variables=variables
        )
        if not response["data"]["executeCommand"]["ok"]:
            desc, reason = response["data"]["executeCommand"]["message"]
            self._exception = DevError(desc=desc, reason=reason)
        return response["data"]["executeCommand"]["output"]
