"""Module for ControllerClient code."""
from __future__ import annotations

from ska_control_model import AdminMode, SimulationMode
from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserver,
)
from tango import DevState

from ska_mid_cbf_int_tests.constants.tango_constants import LRC_ATTR_NAME
from ska_mid_cbf_int_tests.constants.timeout_constants import (
    DEFAULT_DEVICE_TIMEOUT,
    TIMEOUT_MEDIUM,
    TIMEOUT_SHORT,
)

from .device_client import DeviceClient

ADMINMODE_ATTR_NAME = "adminMode"
SIMULATIONMODE_ATTR_NAME = "simulationMode"
STATE_ATTR_NAME = "state"


class ControllerClient(DeviceClient):
    """API Client for controlling the MCS CBF Controller"""

    def __init__(
        self: ControllerClient,
        device_fqdn: str,
        alobserver: AssertiveLoggingObserver,
    ):
        """
        Create instance of ControllerClient.

        :param device_fqdn: FQDN of controller tango device
        :param alobserver: AssertiveLoggingObserver to log to and associate
            events with
        """
        super().__init__(device_fqdn, DEFAULT_DEVICE_TIMEOUT, alobserver)

    def _prep_alobserver_tracer(self: ControllerClient):
        """Subscribe to necessary events for commands of ControllerClient."""
        self.alobserver.subscribe_event_tracer(self.fqdn, ADMINMODE_ATTR_NAME)
        self.alobserver.subscribe_event_tracer(
            self.fqdn, SIMULATIONMODE_ATTR_NAME
        )
        self.alobserver.subscribe_event_tracer(self.fqdn, STATE_ATTR_NAME)
        self.alobserver.subscribe_event_tracer(self.fqdn, LRC_ATTR_NAME)

    def simulation_mode_on(self: ControllerClient):
        """
        Set simulation mode as SimulationMode.TRUE for the controller.

        REQUIRES: admin mode should be offline for a simulation mode change
        to correctly occur.
        """
        self.alobserver.logger.info(
            self._log_wr_attr_msg(
                SIMULATIONMODE_ATTR_NAME, SimulationMode.TRUE
            )
        )
        self.proxy.write_attribute(
            SIMULATIONMODE_ATTR_NAME, SimulationMode.TRUE
        )

    def simulation_mode_off(self: ControllerClient):
        """
        Set simulation mode as SimulationMode.FALSE for the controller.

        REQUIRES: admin mode should be offline for a simulation mode change
        to correctly occur.
        """
        self.alobserver.logger.info(
            self._log_wr_attr_msg(
                SIMULATIONMODE_ATTR_NAME, SimulationMode.FALSE
            )
        )
        self.proxy.write_attribute(
            SIMULATIONMODE_ATTR_NAME, SimulationMode.FALSE
        )

    def admin_mode_online(self: ControllerClient):
        """
        Set admin mode as AdminMode.ONLINE for the controller.
        """
        self.alobserver.logger.info(
            self._log_wr_attr_msg(ADMINMODE_ATTR_NAME, AdminMode.ONLINE)
        )
        self.proxy.write_attribute(ADMINMODE_ATTR_NAME, AdminMode.ONLINE)

    def admin_mode_offline(self: ControllerClient):
        """
        Set admin mode as AdminMode.OFFLINE for the controller.
        """
        self.alobserver.logger.info(
            self._log_wr_attr_msg(ADMINMODE_ATTR_NAME, AdminMode.OFFLINE)
        )
        self.proxy.write_attribute(ADMINMODE_ATTR_NAME, AdminMode.OFFLINE)

    def init_sys_param(self: ControllerClient, init_sys_param_str: str):
        """
        Send given init_sys_param_str to the controller.

        :param init_sys_param_str: json string containing information
            controller initial system parameters according to schema:
            https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/midcbf/initsysparam/index.html
        :raises AssertionError: error if alobserver is ASSERTING and LRC
            ok message is not received
        """
        init_sys_param_cmd_name = "InitSysParam"

        self.alobserver.logger.info(
            self._log_cmd_msg(init_sys_param_cmd_name, init_sys_param_str)
        )

        lrc_result = self.proxy.command_inout(
            init_sys_param_cmd_name, init_sys_param_str
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, init_sys_param_cmd_name, TIMEOUT_SHORT
        )

    def on(self: ControllerClient):
        """
        Turn controller on.

        :raises AssertionError: error if alobserver is ASSERTING and (LRC
            ok message is not received or controller state does not change to
            DevState.ON)
        """
        # pylint: disable=invalid-name
        on_cmd_name = "On"

        self.alobserver.logger.info(self._log_cmd_msg(on_cmd_name))

        lrc_result = self.proxy.command_inout(on_cmd_name)

        self.alobserver.observe_device_attr_change(
            self.fqdn, STATE_ATTR_NAME, DevState.ON, TIMEOUT_MEDIUM
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, on_cmd_name, TIMEOUT_MEDIUM
        )

    def off(self: ControllerClient):
        """
        Turn controller off.

        :raises AssertionError: raises if alobserver is ASSERTING and (LRC
            ok message is not received or controller state does not change to
            DevState.OFF)
        """
        off_cmd_name = "Off"

        lrc_result = self.proxy.command_inout(off_cmd_name)

        self.alobserver.observe_device_attr_change(
            self.fqdn, STATE_ATTR_NAME, DevState.OFF, TIMEOUT_MEDIUM
        )

        self.alobserver.observe_lrc_ok(
            self.fqdn, lrc_result, off_cmd_name, TIMEOUT_MEDIUM
        )
