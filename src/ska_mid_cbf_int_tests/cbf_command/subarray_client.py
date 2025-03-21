"""Module for SubarrayClient code."""
from __future__ import annotations

import time
from typing import List

from ska_control_model import ObsState
from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserver,
)

from ska_mid_cbf_int_tests.constants.tango_constants import LRC_ATTR_NAME
from ska_mid_cbf_int_tests.constants.timeout_constants import (
    DEFAULT_DEVICE_TIMEOUT,
    TIMEOUT_LONG,
    TIMEOUT_SHORT,
)

from .device_client import DeviceClient

OBSSTATE_ATTR_NAME = "obsstate"
RECEPTORS_ATTR_NAME = "receptors"


class SubarrayClient(DeviceClient):
    """
    API Client for controlling an MCS subarray device. Implemented commands
    generally follow
    https://developer.skao.int/projects/ska-mid-cbf-mcs/en/latest/guide/interfaces/lmc_mcs_interface.html
    and for success observing states should follow state machine in
    https://developer.skao.int/projects/ska-control-model/en/latest/obs_state.html
    """

    def __init__(
        self: SubarrayClient,
        device_fqdn: str,
        alobserver: AssertiveLoggingObserver,
    ):
        """
        Create instance of SubarrayClient.

        :param device_fqdn: FQDN of subarray tango device
        :param alobserver: AssertiveLoggingObserver to log to and associate
            events with
        """
        super().__init__(device_fqdn, DEFAULT_DEVICE_TIMEOUT, alobserver)

    def _prep_alobserver_tracer(self: SubarrayClient):
        """Subscribe to necessary events for commands of SubarrayClient."""
        self.alobserver.subscribe_event_tracer(self.fqdn, OBSSTATE_ATTR_NAME)
        self.alobserver.subscribe_event_tracer(self.fqdn, LRC_ATTR_NAME)

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
            if self.get_obsstate() not in obs_states_to_exit:
                return True
            time.sleep(delay_between_read_sec)
        if self.get_obsstate() not in obs_states_to_exit:
            return True
        self.alobserver.logger.error(
            f"{self.fqdn}: Timeout waiting to exit one of states: "
            f"{obs_states_to_exit}"
        )
        self.alobserver.logger.error(
            f"{self.fqdn}: Final state was: {self.get_obsstate()}"
        )
        return False

    def get_obsstate(self: SubarrayClient) -> ObsState:
        """
        Get current ObsState of subarray.

        :returns: current ObsState of subarray.
        """
        return self.proxy.read_attribute(OBSSTATE_ATTR_NAME).value

    def get_receptors(self: SubarrayClient) -> List[str]:
        """
        Get current receptors assigned to subarray.

        :returns: current receptors assigned to subarray.
        """
        return list(self.proxy.read_attribute(RECEPTORS_ATTR_NAME).value)

    def add_receptors(self: SubarrayClient, receptors: List[str]):
        """
        Add given receptors to the subarray. On success, subarray should go to
        ObsState.IDLE.

        :param receptors: list of receptors to add to the subarray. Receptors
            must match dish receptor id format associated with dish_mapping of
            a relevant schema in
            https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/midcbf/initsysparam/index.html
        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.IDLE or LRC ok message is not received)
        """
        add_receptors_cmd_name = "AddReceptors"

        self.alobserver.logger.info(
            self._log_cmd_msg(add_receptors_cmd_name, receptors)
        )

        lrc_result = self.proxy.command_inout(
            add_receptors_cmd_name, receptors
        )

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.IDLE, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, add_receptors_cmd_name, TIMEOUT_LONG
        )

    def remove_receptors(self: SubarrayClient, receptors: List[str]):
        """
        Remove given receptors from the subarray. On success, subarray should
        go to ObsState.IDLE if not all receptors are removed or ObsState.EMPTY
        if all receptors are removed.

        :param receptors: list of receptors to remove from the subarray.
            Receptors must match dish receptor id format associated with
            dish_mapping of a relevant schema in
            https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/midcbf/initsysparam/index.html
        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.EMPTY/IDLE or LRC ok message is not
            received)
        """
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

        self.alobserver.observe_device_attr_change(
            self.fqdn,
            OBSSTATE_ATTR_NAME,
            ObsState.EMPTY if going_to_empty else ObsState.IDLE,
            TIMEOUT_SHORT,
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, remove_receptors_cmd_name, TIMEOUT_LONG
        )

    def remove_all_receptors(self: SubarrayClient):
        """
        Remove all receptors from the subarray. On success, subarray should
        go to ObsState.EMPTY.

        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.EMPTY or LRC ok message is not
            received)
        """
        remove_all_receptors_cmd_name = "RemoveAllReceptors"

        self.alobserver.logger.info(
            self._log_cmd_msg(remove_all_receptors_cmd_name)
        )

        lrc_result = self.proxy.command_inout(remove_all_receptors_cmd_name)

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.EMPTY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, remove_all_receptors_cmd_name, TIMEOUT_LONG
        )

    def configure_scan(self: SubarrayClient, configure_str: str):
        """
        Configure the scan of the subarray. On success, subarray should go to
        ObsState.READY.

        :param configure_str: json string containing configuration for subarray
            to configure scan to. Format and info should be according to a
            supported schema in
            https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/csp/mid/configurescan/index.html
        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.READY or LRC ok message is not
            received)
        """
        configure_scan_cmd_names = "ConfigureScan"

        self.alobserver.logger.info(
            self._log_cmd_msg(configure_scan_cmd_names, configure_str)
        )

        lrc_result = self.proxy.command_inout(
            configure_scan_cmd_names, configure_str
        )

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.READY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, configure_scan_cmd_names, TIMEOUT_SHORT
        )

    def scan(self: SubarrayClient, scan_str: str):
        """
        Starts the scan of the subarray. On success, subarray should go to
        ObsState.SCANNING.

        :param configure_str: json string containing scan info. Format and info
            should be according to a supported schema in
            https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/csp/mid/scan/index.html
        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.SCANNING or LRC ok message is not
            received)
        """
        scan_cmd_name = "Scan"

        self.alobserver.logger.info(self._log_cmd_msg(scan_cmd_name, scan_str))

        lrc_result = self.proxy.command_inout(scan_cmd_name, scan_str)

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.SCANNING, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, scan_cmd_name, TIMEOUT_SHORT
        )

    def end_scan(self: SubarrayClient):
        """
        Ends the scan of the subarray. On success, subarray should go to
        ObsState.READY.

        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.READY or LRC ok message is not
            received)
        """
        end_scan_cmd_name = "EndScan"

        self.alobserver.logger.info(self._log_cmd_msg(end_scan_cmd_name))

        lrc_result = self.proxy.command_inout(end_scan_cmd_name)

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.READY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, end_scan_cmd_name, TIMEOUT_SHORT
        )

    def go_to_idle(self: SubarrayClient):
        """
        Sends the subarray to idle. On success, subarray should go to
        ObsState.IDLE.

        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.IDLE or LRC ok message is not
            received)
        """
        go_to_idle_cmd_name = "GoToIdle"

        self.alobserver.logger.info(self._log_cmd_msg(go_to_idle_cmd_name))

        lrc_result = self.proxy.command_inout(go_to_idle_cmd_name)

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.IDLE, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, go_to_idle_cmd_name, TIMEOUT_SHORT
        )

    def abort(self: SubarrayClient):
        """
        Aborts current stage of subarray from
        ObsState.IDLE/CONFIGURING/READY/SCANNING. On success, subarray should
        go to ObsState.ABORTED.

        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.ABORTED or LRC ok message is not
            received)
        """
        abort_cmd_name = "Abort"

        self.alobserver.logger.info(self._log_cmd_msg(abort_cmd_name))

        lrc_result = self.proxy.command_inout(abort_cmd_name)

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.ABORTED, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, abort_cmd_name, TIMEOUT_SHORT
        )

    def obsreset(self: SubarrayClient):
        """
        Resets current stage of subarray from ObsState.FAULT/ABORTED keeping
        assigned receptors. On success, subarray should go to ObsState.IDLE.

        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.IDLE or LRC ok message is not
            received)
        """
        obsreset_cmd_name = "ObsReset"

        self.alobserver.logger.info(self._log_cmd_msg(obsreset_cmd_name))

        lrc_result = self.proxy.command_inout(obsreset_cmd_name)

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.IDLE, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, obsreset_cmd_name, TIMEOUT_SHORT
        )

    def restart(self: SubarrayClient):
        """
        Restarts current stage of subarray from ObsState.FAULT/ABORTED not
        keeping assigned receptors. On success, subarray should go to
        ObsState.EMPTY.

        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to ObsState.ABORTED or LRC ok message is not
            received)
        """
        restart_cmd_name = "Restart"

        self.alobserver.logger.info(self._log_cmd_msg(restart_cmd_name))

        lrc_result = self.proxy.command_inout(restart_cmd_name)

        self.alobserver.observe_device_attr_change(
            self.fqdn, OBSSTATE_ATTR_NAME, ObsState.EMPTY, TIMEOUT_SHORT
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, restart_cmd_name, TIMEOUT_SHORT
        )

    def send_to_empty(self: SubarrayClient):
        """
        Follows observing state machine
        https://developer.skao.int/projects/ska-control-model/en/latest/obs_state.html
        to bring subarray to ObsState.EMPTY from any current observing state.

        :raises AssertionError: error if alobserver is ASSERTING and (subarray
            does not change to expected state or LRC ok message is not
            received)
        """
        exiting_wait_time_sec = TIMEOUT_SHORT

        if self.get_obsstate() == ObsState.READY:
            self.go_to_idle()

        if self.get_obsstate() == ObsState.IDLE:
            self.remove_all_receptors()

        if self.get_obsstate() in [ObsState.RESOURCING, ObsState.RESTARTING]:
            self._wait_to_exit_obs_states(
                [ObsState.RESOURCING, ObsState.RESTARTING],
                exiting_wait_time_sec,
            )

        # Take abort restart path if not in EMPTY yet
        if self.get_obsstate() != ObsState.EMPTY:

            # Ensure not in erroring transition state
            if self.get_obsstate() in [ObsState.ABORTING, ObsState.RESETTING]:
                self._wait_to_exit_obs_states(
                    [ObsState.ABORTING, ObsState.RESETTING],
                    exiting_wait_time_sec,
                )

            # Ensure in restartable state
            if self.get_obsstate() not in [ObsState.FAULT, ObsState.ABORTED]:
                self.abort()

            self.restart()
