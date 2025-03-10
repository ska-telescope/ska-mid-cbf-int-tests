"""TODO"""
from __future__ import annotations

from typing import List

from ska_control_model import ObsState

from constants.timeout_constants import TIMEOUT_LONG, TIMEOUT_SHORT

from .device_client import DeviceClient

OBS_STATE_ATTR_NAME = "obsState"


class SubarrayClient(DeviceClient):
    """TODO"""

    def add_receptors(self: SubarrayClient, receptors: List[str]):
        """TODO"""
        add_receptors_cmd_name = "AddReceptors"

        self.alobserver.logger.info(
            self._log_msg(add_receptors_cmd_name, receptors)
        )

        lrc_result = self.proxy.command_inout(
            add_receptors_cmd_name, receptors
        )

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.IDLE, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, add_receptors_cmd_name, TIMEOUT_LONG
        )

    def remove_receptors(self: SubarrayClient, receptors: List[str]):
        """TODO"""
        remove_receptors_cmd_name = "RemoveReceptors"

        self.alobserver.logger.info(
            self._log_msg(remove_receptors_cmd_name, receptors)
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
        """TODO"""
        remove_all_receptors_cmd_name = "RemoveAllReceptors"

        self.alobserver.logger.info(
            self._log_msg(remove_all_receptors_cmd_name)
        )

        lrc_result = self.proxy.command_inout(remove_all_receptors_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.EMPTY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, remove_all_receptors_cmd_name, TIMEOUT_LONG
        )

    def configure_scan(self: SubarrayClient, configure_str: str):
        """TODO"""
        configure_scan_cmd_names = "ConfigureScan"

        self.alobserver.logger.info(
            self._log_msg(configure_scan_cmd_names, configure_str)
        )

        lrc_result = self.proxy.command_inout(
            configure_scan_cmd_names, configure_str
        )

        self.alobserver.observe_device_state_change(
            self.fqdn, OBS_STATE_ATTR_NAME, ObsState.READY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, configure_scan_cmd_names, TIMEOUT_SHORT
        )

    def scan(self: SubarrayClient, scan_str: str):
        """TODO"""
        scan_cmd_name = "Scan"

        self.alobserver.logger.info(self._log_msg(scan_cmd_name, scan_str))

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
        """TODO"""
        end_scan_cmd_name = "EndScan"

        self.alobserver.logger.info(self._log_msg(end_scan_cmd_name))

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
        """TODO"""
        go_to_idle_name = "GoToIdle"

        self.alobserver.logger.info(self._log_msg(go_to_idle_name))

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
