"""Module for DeviceClient code."""
from __future__ import annotations

import abc
from typing import Any

from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserver,
)
from tango import DeviceProxy


class DeviceClient(abc.ABC):
    """Base Client for Tango Device"""

    # pylint: disable=too-few-public-methods
    def __init__(
        self: DeviceClient,
        device_fqdn: str,
        device_timeout_sec: float,
        alobserver: AssertiveLoggingObserver,
    ):
        """
        Create instance of DeviceClient setting up a tango.DeviceProxy with
        timeout device_timeout_sec and subscribing clients with the
        event_tracer of given AssertiveLoggingObserver alobserver for relevant
        LRC and state change event tracing.

        :param device_fqdn: fully qualified device name (fqdn) to generate
            proxy towards
        :param device_timeout_sec: timeout for proxy
        :param alobserver: AssertiveLoggingObserver to log to and associate
            events with
        """
        self.fqdn = device_fqdn
        self.proxy = DeviceProxy(self.fqdn)
        # Set seperately using set_timeout_millis to due tango bug with setting
        # in constructor
        self.proxy.set_timeout_millis(int(device_timeout_sec * 1000))
        self.alobserver = alobserver

        # Call concrete alobserver tracer to associate events with alobserver
        self._prep_alobserver_tracer()

    @abc.abstractmethod
    def _prep_alobserver_tracer(self: DeviceClient):
        """
        Subscribe for the relevant events of the commands of the DeviceClient
        to the event_tracer of the DeviceClient's alobserver.
        """

    def _log_wr_attr_msg(
        self: DeviceClient, attr_name: str, attr_val: Any
    ) -> str:
        """Create standardized attribute write log message."""
        return f"{self.fqdn} {attr_name} (write: {attr_val})"

    def _log_cmd_msg(
        self: DeviceClient, cmd_name: str, cmd_param: Any = None
    ) -> str:
        """Create standardized command call log message."""
        log_str = f"{self.fqdn} {cmd_name}"
        if cmd_param is not None:
            max_cmd_param_msg_len = 500
            cmd_param_str = str(cmd_param)
            if len(cmd_param_str) > max_cmd_param_msg_len:
                cmd_param_str = cmd_param_str[:max_cmd_param_msg_len] + " ..."
            log_str += f" (cmd_param: {cmd_param_str})"
        return log_str
