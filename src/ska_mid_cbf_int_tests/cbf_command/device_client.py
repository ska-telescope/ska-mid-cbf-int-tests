"""TODO"""
from __future__ import annotations

import abc
from typing import Any

from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserver,
)
from tango import DeviceProxy


class DeviceClient(abc.ABC):
    """TODO"""

    # pylint: disable=too-few-public-methods
    def __init__(
        self: DeviceClient,
        device_fqdn: str,
        device_timeout_sec: float,
        alobserver: AssertiveLoggingObserver,
    ):
        self.fqdn = device_fqdn
        self.proxy = DeviceProxy(self.fqdn)
        self.proxy.set_timeout_millis(int(device_timeout_sec * 1000))
        self.alobserver = alobserver

    def _log_wr_attr_msg(
        self: DeviceClient, attr_name: str, attr_val: Any
    ) -> str:
        """TODO"""
        return f"{self.fqdn} {attr_name} (write: {attr_val})"

    def _log_cmd_msg(
        self: DeviceClient, cmd_name: str, cmd_param: Any = None
    ) -> str:
        """TODO"""
        log_str = f"{self.fqdn} {cmd_name}"
        if cmd_param is not None:
            max_cmd_param_msg_len = 500
            cmd_param_str = str(cmd_param)
            if len(cmd_param_str) > max_cmd_param_msg_len:
                cmd_param_str = cmd_param_str[:max_cmd_param_msg_len] + " ..."
            log_str += f" (cmd_param: {cmd_param_str})"
        return log_str
