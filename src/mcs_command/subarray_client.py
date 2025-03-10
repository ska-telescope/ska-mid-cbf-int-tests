"""s"""
from __future__ import annotations

from typing import Any, List

from assertive_logging_observer import AssertiveLoggingObserver
from ska_control_model import ObsState
from tango import DeviceProxy

from constants.timeout_constants import TIMEOUT_LONG, TIMEOUT_SHORT

OBS_STATE_ATTR_NAME = "obsState"


class SubarrayClient:
    """s"""

    def __init__(
        self: SubarrayClient,
        subarray_fqdn: str,
        alobserver: AssertiveLoggingObserver,
    ):
        self.fqdn = subarray_fqdn
        self.proxy = DeviceProxy(self.fqdn)
        self.alobserver = alobserver

    def _subarray_log_msg(
        self: SubarrayClient, subarray_cmd_name: str, input_str: Any = None
    ) -> str:
        """s"""
        log_str = f"{self.fqdn} {subarray_cmd_name}"
        if input_str is not None:
            log_str += f" (cmd_param: {input_str})"
        return log_str

    def add_receptors(self: SubarrayClient, receptors: List[str]):
        """s"""
        add_receptors_cmd_name = "AddReceptors"

        self.alobserver.logger.info(
            self._subarray_log_msg(add_receptors_cmd_name, receptors)
        )

        lrc_result = self.proxy.command_inout(
            add_receptors_cmd_name, receptors
        )

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBS_STATE_ATTR_NAME,
            ObsState.IDLE,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, add_receptors_cmd_name, TIMEOUT_LONG
        )

    def remove_receptors(self: SubarrayClient, receptors: List[str]):
        """s"""
        remove_receptors_cmd_name = "RemoveReceptors"

        self.alobserver.logger.info(
            self._subarray_log_msg(remove_receptors_cmd_name, receptors)
        )

        going_to_empty = set(receptors) == set(
            self.proxy.read_attribute("receptors").value
        )

        lrc_result = self.proxy.command_inout(
            remove_receptors_cmd_name, receptors
        )

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBS_STATE_ATTR_NAME,
            ObsState.EMPTY if going_to_empty else ObsState.IDLE,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, remove_receptors_cmd_name, TIMEOUT_LONG
        )

    def remove_all_receptors(self: SubarrayClient):
        """s"""
        remove_all_receptors_cmd_name = "RemoveAllReceptors"

        self.alobserver.logger.info(
            self._subarray_log_msg(remove_all_receptors_cmd_name)
        )

        lrc_result = self.proxy.command_inout(remove_all_receptors_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBS_STATE_ATTR_NAME,
            ObsState.EMPTY,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, remove_all_receptors_cmd_name, TIMEOUT_LONG
        )

    def configure_scan(self: SubarrayClient, configure_str: str):
        """s"""
        configure_scan_cmd_names = "ConfigureScan"

        self.alobserver.logger.info(
            self._subarray_log_msg(configure_scan_cmd_names, configure_str)
        )

        lrc_result = self.proxy.command_inout(
            configure_scan_cmd_names, configure_str
        )

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBS_STATE_ATTR_NAME,
            ObsState.READY,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, configure_scan_cmd_names, TIMEOUT_SHORT
        )

    def scan(self: SubarrayClient, scan_str: str):
        """s"""
        scan_cmd_name = "Scan"

        self.alobserver.logger.info(
            self._subarray_log_msg(scan_cmd_name, scan_str)
        )

        lrc_result = self.proxy.command_inout(scan_cmd_name, scan_str)

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBS_STATE_ATTR_NAME,
            ObsState.SCANNING,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, scan_cmd_name, TIMEOUT_SHORT
        )

    def end_scan(self: SubarrayClient):
        """s"""
        end_scan_cmd_name = "EndScan"

        self.alobserver.logger.info(self._subarray_log_msg(end_scan_cmd_name))

        lrc_result = self.proxy.command_inout(end_scan_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBS_STATE_ATTR_NAME,
            ObsState.READY,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, end_scan_cmd_name, TIMEOUT_SHORT
        )

    def go_to_idle(self: SubarrayClient):
        """s"""
        go_to_idle_name = "GoToIdle"

        self.alobserver.logger.info(self._subarray_log_msg(go_to_idle_name))

        lrc_result = self.proxy.command_inout(go_to_idle_name)

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBS_STATE_ATTR_NAME,
            ObsState.IDLE,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, go_to_idle_name, TIMEOUT_SHORT
        )
