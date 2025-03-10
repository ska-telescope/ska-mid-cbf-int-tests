"""TODO"""
from __future__ import annotations

from tango import DevState

from constants.timeout_constants import TIMEOUT_MEDIUM, TIMEOUT_SHORT

from .device_client import DeviceClient

STATE_ATTR_NAME = "state"


class ControllerClient(DeviceClient):
    """TODO"""

    def init_sys_param(self: ControllerClient, init_sys_param_str: str):
        """TODO"""
        init_sys_param_cmd_name = "InitSysParam"

        self.alobserver.logger.info(
            self._log_msg(init_sys_param_cmd_name, init_sys_param_str)
        )

        lrc_result = self.proxy.command_inout(
            init_sys_param_cmd_name, init_sys_param_str
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, init_sys_param_cmd_name, TIMEOUT_SHORT
        )

    def on(self: ControllerClient):
        """TODO"""
        # pylint: disable=invalid-name
        on_cmd_name = "On"

        self.alobserver.logger.info(self._log_msg(on_cmd_name))

        lrc_result = self.proxy.command_inout(on_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn, STATE_ATTR_NAME, DevState.ON, TIMEOUT_MEDIUM
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, on_cmd_name, TIMEOUT_MEDIUM
        )

    def off(self: ControllerClient):
        """TODO"""
        off_cmd_name = "Off"

        lrc_result = self.proxy.command_inout(off_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn, STATE_ATTR_NAME, DevState.OFF, TIMEOUT_MEDIUM
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, off_cmd_name, TIMEOUT_MEDIUM
        )
