from __future__ import annotations

from typing import Any, List

from tango import DeviceProxy
from ska_control_model import ObsState

from assertive_logging_observer import AssertiveLoggingObserver

from timeout_constants import (
    TIMEOUT_INSTANT,
    TIMEOUT_SHORT,
    TIMEOUT_MEDIUM,
    TIMEOUT_LONG,
)

OBS_STATE_ATTR_NAME = "obsState"


class SubarrayClient:

    def __init__(
        self: SubarrayClient,
        subarray_fqdn: str,
        alobserver: AssertiveLoggingObserver
    ):
        self.fqdn = subarray_fqdn
        self.proxy = DeviceProxy(self.fqdn)
        self.alobserver = alobserver

    def _subarray_log_msg(
        self: SubarrayClient,
        subarray_cmd_name: str,
        input_str: Any = None
    ) -> str:
        log_str = f"{self.fqdn} {subarray_cmd_name}"
        if input_str is not None:
            log_str += f" (cmd_param: {input_str})"
        return log_str

    def add_receptors(self: SubarrayClient, receptors: List[str]):
        
        ADD_RECEPTORS_CMD_NAME = "AddReceptors"

        self.alobserver.logger.info(
            self._subarray_log_msg(ADD_RECEPTORS_CMD_NAME, receptors)
        )

        lrc_result = self.proxy.command_inout(
            ADD_RECEPTORS_CMD_NAME, receptors
        )

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.IDLE, TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, ADD_RECEPTORS_CMD_NAME, TIMEOUT_LONG
        )


    def remove_receptors(self: SubarrayClient, receptors: List[str]):
        
        REMOVE_RECEPTORS_CMD_NAME = "RemoveReceptors"

        self.alobserver.logger.info(
            self._subarray_log_msg(REMOVE_RECEPTORS_CMD_NAME, receptors)
        )

        going_to_empty = (
            set(receptors) == set(self.proxy.read_attribute("receptors").value)
        )

        lrc_result = self.proxy.command_inout(
            REMOVE_RECEPTORS_CMD_NAME, receptors
        )

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBS_STATE_ATTR_NAME,
            ObsState.EMPTY if going_to_empty else ObsState.IDLE,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, REMOVE_RECEPTORS_CMD_NAME, TIMEOUT_LONG
        )


    def remove_all_receptors(self: SubarrayClient):

        REMOVE_ALL_RECEPTORS_CMD_NAME = "RemoveAllReceptors"

        self.alobserver.logger.info(
            self._subarray_log_msg(REMOVE_ALL_RECEPTORS_CMD_NAME)
        )

        lrc_result = self.proxy.command_inout(
            REMOVE_ALL_RECEPTORS_CMD_NAME
        )

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.EMPTY, TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, REMOVE_ALL_RECEPTORS_CMD_NAME, TIMEOUT_LONG
        )


    def configure_scan(self: SubarrayClient, configure_str: str):
        
        CONFIGURE_SCAN_CMD_NAME = "ConfigureScan"

        self.alobserver.logger.info(
            self._subarray_log_msg(CONFIGURE_SCAN_CMD_NAME, configure_str)
        )

        lrc_result = self.proxy.command_inout(
            CONFIGURE_SCAN_CMD_NAME, configure_str
        )

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.READY, TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, CONFIGURE_SCAN_CMD_NAME, TIMEOUT_SHORT
        )

    def scan(self: SubarrayClient, scan_str: str):

        SCAN_CMD_NAME = "Scan"

        self.alobserver.logger.info(
            self._subarray_log_msg(SCAN_CMD_NAME, scan_str)
        )

        lrc_result = self.proxy.command_inout(SCAN_CMD_NAME, scan_str)

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.SCANNING, TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, SCAN_CMD_NAME, TIMEOUT_SHORT
        )

    def end_scan(self: SubarrayClient):

        END_SCAN_CMD_NAME = "EndScan"

        self.alobserver.logger.info(self._subarray_log_msg(END_SCAN_CMD_NAME))

        lrc_result = self.proxy.command_inout(END_SCAN_CMD_NAME)

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.READY, TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, END_SCAN_CMD_NAME, TIMEOUT_SHORT
        )

    def go_to_idle(self: SubarrayClient):

        GO_TO_IDLE_CMD_NAME = "GoToIdle"

        self.alobserver.logger.info(
            self._subarray_log_msg(GO_TO_IDLE_CMD_NAME)
        )

        lrc_result = self.proxy.command_inout(GO_TO_IDLE_CMD_NAME)

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.IDLE, TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, GO_TO_IDLE_CMD_NAME, TIMEOUT_SHORT
        )
