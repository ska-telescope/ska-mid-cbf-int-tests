"""Tango device proxy-based client."""

from typing import Any, List, Optional

try:
    import tango
except ImportError:
    tango = None

from .base import TangoClient


class TangoClientDP(TangoClient):
    """
    Client for a Tango device using Python Tango DeviceProxy

    :param device: name of device
    :param translations: optional translations for attribute values
    """

    def __init__(self, device: str, translations: Optional[dict] = None):
        super().__init__(device, translations=translations)
        self._proxy = tango.DeviceProxy(device)

    def get_commands(self) -> Optional[List[str]]:
        """
        Get list of commands from device.

        :returns: list of command names

        """
        try:
            commands = self._proxy.get_command_list()
        except tango.DevFailed as exc:
            self._exception = exc.args[0]
            commands = None
        return commands

    def fetch_attribute_names(self) -> Optional[List[str]]:
        """
        Get list of attributes from device.

        :returns: list of attribute names

        """
        try:
            attributes = self._proxy.get_attribute_list()
        except tango.DevFailed as exc:
            self._exception = exc.args[0]
            attributes = None
        return attributes

    def get_attribute(self, attribute: str) -> Any:
        """
        Get value of device attribute.

        :param attribute: name of attribute
        :returns: value of attribute

        """
        try:
            value = self._proxy.read_attribute(attribute)
            if attribute.lower() == "state":
                value = value.value.name
            else:
                value = self._translate_attribute(attribute, value.value)
        except tango.DevFailed as exc:
            self._exception = exc.args[0]
            value = None
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
        try:
            retval = self._proxy.command_inout(command, cmd_param=argument)
        except tango.DevFailed as exc:
            self._exception = exc.args[0]
            retval = None
        return retval
