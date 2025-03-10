"""TODO"""
from __future__ import annotations

from typing import Any

from assertive_logging_observer import AssertiveLoggingObserver
from tango import DeviceProxy


class DeviceClient:
    """TODO"""

    # pylint: disable=too-few-public-methods
    def __init__(
        self: DeviceClient,
        device_fqdn: str,
        alobserver: AssertiveLoggingObserver,
    ):
        self.fqdn = device_fqdn
        self.proxy = DeviceProxy(self.fqdn)
        self.alobserver = alobserver

    def _log_msg(
        self: DeviceClient, subarray_cmd_name: str, cmd_param: Any = None
    ) -> str:
        """TODO"""
        log_str = f"{self.fqdn} {subarray_cmd_name}"
        if input is not None:
            log_str += f" (cmd_param: {cmd_param})"
        return log_str
