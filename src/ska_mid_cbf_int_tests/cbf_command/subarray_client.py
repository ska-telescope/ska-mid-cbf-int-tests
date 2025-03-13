"""TODO"""
from __future__ import annotations

import time
from typing import List

from assertive_logging_observer import AssertiveLoggingObserver
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer

from ska_mid_cbf_int_tests.constants.tango_constants import LRC_ATTR_NAME
from ska_mid_cbf_int_tests.constants.timeout_constants import (
    DEFAULT_DEVICE_TIMEOUT,
    TIMEOUT_LONG,
    TIMEOUT_SHORT,
)

from .device_client import DeviceClient

OBSSTATE_ATTR_NAME = "obsstate"


class SubarrayClient(DeviceClient):
    """TODO"""

    def __init__(
        self: SubarrayClient,
        device_fqdn: str,
        alobserver: AssertiveLoggingObserver,
    ):
        super().__init__(device_fqdn, DEFAULT_DEVICE_TIMEOUT, alobserver)

    def _wait_to_exit_obs_states(
        self: SubarrayClient,
        obs_states_to_exit: List[str],
        max_wait_time_sec: float,
        delay_between_read_sec: float = 1,
    ) -> bool:
        """
        Checks if the subarray is in states obs_states_to_exit and waits
        max_wait_time_sec for subarray to exit states, waiting
        delay_between_read_sec in between exit checks.

        Args:
        :param obs_state_to_exit: list of observing states to exit
        :param max_wait_time_sec: max time to wait for the subarray to exit
            the specified states (seconds)
        :param delay_between_read_sec: how long to wait between checks
            (seconds)
        :rtype bool: boolean indicating if the subarray exited states
            successfully
        """
        end_time = time.time() + max_wait_time_sec
        while time.time() < end_time:
            if (
                self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value
                not in obs_states_to_exit
            ):
                return True
            time.sleep(delay_between_read_sec)
        if (
            self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value
            not in obs_states_to_exit
        ):
            return True
        self.alobserver.logger.error(
            f"{self.fqdn}: Timeout waiting to exit one of states: "
            f"{obs_states_to_exit}"
        )
        self.alobserver.logger.error(
            f"{self.fqdn}: Final state was: "
            f"{self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value}"
        )
        return False

    def prep_event_tracer(
        self: SubarrayClient, event_tracer: TangoEventTracer
    ):
        """TODO"""
        event_tracer.subscribe_event(self.fqdn, OBSSTATE_ATTR_NAME)
        event_tracer.subscribe_event(self.fqdn, LRC_ATTR_NAME)

    def add_receptors(self: SubarrayClient, receptors: List[str]):
        """TODO"""
        add_receptors_cmd_name = "AddReceptors"

        self.alobserver.logger.info(
            self._log_cmd_msg(add_receptors_cmd_name, receptors)
        )

        lrc_result = self.proxy.command_inout(
            add_receptors_cmd_name, receptors
        )

        self.alobserver.observe_device_state_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.IDLE, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, add_receptors_cmd_name, TIMEOUT_LONG
        )

    def remove_receptors(self: SubarrayClient, receptors: List[str]):
        """TODO"""
        remove_receptors_cmd_name = "RemoveReceptors"

        self.alobserver.logger.info(
            self._log_cmd_msg(remove_receptors_cmd_name, receptors)
        )

        going_to_empty = set(receptors) == set(
            self.proxy.read_attribute("receptors").value
        )

        lrc_result = self.proxy.command_inout(
            remove_receptors_cmd_name, receptors
        )

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBSSTATE_ATTR_NAME,
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
            self._log_cmd_msg(remove_all_receptors_cmd_name)
        )

        lrc_result = self.proxy.command_inout(remove_all_receptors_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.EMPTY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, remove_all_receptors_cmd_name, TIMEOUT_LONG
        )

    def configure_scan(self: SubarrayClient, configure_str: str):
        """TODO"""
        configure_scan_cmd_names = "ConfigureScan"

        self.alobserver.logger.info(
            self._log_cmd_msg(configure_scan_cmd_names, configure_str)
        )

        lrc_result = self.proxy.command_inout(
            configure_scan_cmd_names, configure_str
        )

        self.alobserver.observe_device_state_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.READY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, configure_scan_cmd_names, TIMEOUT_SHORT
        )

    def scan(self: SubarrayClient, scan_str: str):
        """TODO"""
        scan_cmd_name = "Scan"

        self.alobserver.logger.info(self._log_cmd_msg(scan_cmd_name, scan_str))

        lrc_result = self.proxy.command_inout(scan_cmd_name, scan_str)

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBSSTATE_ATTR_NAME,
            ObsState.SCANNING,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, scan_cmd_name, TIMEOUT_SHORT
        )

    def end_scan(self: SubarrayClient):
        """TODO"""
        end_scan_cmd_name = "EndScan"

        self.alobserver.logger.info(self._log_cmd_msg(end_scan_cmd_name))

        lrc_result = self.proxy.command_inout(end_scan_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn,
            OBSSTATE_ATTR_NAME,
            ObsState.READY,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, end_scan_cmd_name, TIMEOUT_SHORT
        )

    def go_to_idle(self: SubarrayClient):
        """TODO"""
        go_to_idle_cmd_name = "GoToIdle"

        self.alobserver.logger.info(self._log_cmd_msg(go_to_idle_cmd_name))

        lrc_result = self.proxy.command_inout(go_to_idle_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.IDLE, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, go_to_idle_cmd_name, TIMEOUT_SHORT
        )

    def abort(self: SubarrayClient):
        """TODO"""
        abort_cmd_name = "Abort"

        self.alobserver.logger.info(self._log_cmd_msg(abort_cmd_name))

        lrc_result = self.proxy.command_inout(abort_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.ABORTED, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, abort_cmd_name, TIMEOUT_SHORT
        )

    def reset(self: SubarrayClient):
        """TODO"""
        reset_cmd_name = "Reset"

        self.alobserver.logger.info(self._log_cmd_msg(reset_cmd_name))

        lrc_result = self.proxy.command_inout(reset_cmd_name)

        self.alobserver.observe_device_state_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.EMPTY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_result(
            self.fqdn, lrc_result, reset_cmd_name, TIMEOUT_SHORT
        )

    def send_to_empty(self: SubarrayClient):
        """TODO"""
        exiting_wait_time_sec = TIMEOUT_SHORT

        if (
            self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value
            == ObsState.READY
        ):
            self.go_to_idle()

        if (
            self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value
            == ObsState.IDLE
        ):
            self.remove_all_receptors()

        if self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value in [
            ObsState.RESOURCING,
            ObsState.RESTARTING,
        ]:
            self._wait_to_exit_obs_states(
                [ObsState.RESOURCING, ObsState.RESTARTING],
                exiting_wait_time_sec,
            )

        # Take abort reset path if not in EMPTY yet
        if (
            self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value
            != ObsState.EMPTY
        ):

            # Ensure not in erroring transition state
            if self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value in [
                ObsState.ABORTING,
                ObsState.RESETTING,
            ]:
                self._wait_to_exit_obs_states(
                    [ObsState.ABORTING, ObsState.RESETTING],
                    exiting_wait_time_sec,
                )

            # Ensure in resettable state
            if self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value in [
                ObsState.FAULT,
                ObsState.ABORTED,
            ]:
                self.abort()

            self.reset()
