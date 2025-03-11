"""Tango client base class."""

from typing import Any, List, Optional


class TangoClient:
    """
    Base class for Tango device clients.

    :param device: name of device
    :param translations: optional translations for attribute values
    """

    def __init__(self, device: str, translations: Optional[dict] = None):
        self._device = device
        self._translations = translations
        self._exception = None

    @property
    def exception(self) -> Optional[Exception]:
        """Get the stored exception."""
        return self._exception

    def clear_exception(self):
        """Clear the stored exception."""
        self._exception = None

    def _translate_attribute(self, attribute: str, value: Any) -> Any:
        """
        Translate attribute value.

        :param attribute: attribute name
        :param value: attribute value
        :returns: translated attribute value

        """
        if self._translations and attribute in self._translations:
            value = self._translations[attribute][value]
        return value

    def get_commands(self) -> Optional[List[str]]:
        """
        Get list of commands from device.

        :returns: list of command names

        """
        raise NotImplementedError()

    def get_attribute(self, attribute: str) -> Any:
        """
        Get value of device attribute.

        :param attribute: name of attribute
        :returns: value of attribute

        """
        raise NotImplementedError()

    def execute_command(
        self, command: str, argument: Optional[str] = None
    ) -> Any:
        """
        Execute command.

        :param command: name of command
        :param argument: optional argument for command
        :returns: return value of command

        """
        raise NotImplementedError()
