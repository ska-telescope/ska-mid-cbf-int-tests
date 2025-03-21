"""SubarrayClient testing."""

from __future__ import annotations

import importlib.resources as res

import pytest
from ska_control_model import ObsState

import ska_mid_cbf_int_tests.data.configure_scan as configure_scan_data
import ska_mid_cbf_int_tests.data.scan as scan_data
from ska_mid_cbf_int_tests.cbf_command import SubarrayClient
from ska_mid_cbf_int_tests.constants.tango_constants import gen_subarray_fqdn

from ..test_lib.test_packages import DeviceClientPkg, RecordingPkg


class TestSubarrayClient:
    """Tests command sequencing and functionality of SubarrayClient."""

    @classmethod
    def setup_class(cls: TestSubarrayClient):
        """Read in dummy_configure_scan str and dummy_scan str."""

        conf_scan_json_file = res.files(configure_scan_data).joinpath(
            "dummy_configure_scan.json"
        )
        cls.conf_scan_str = conf_scan_json_file.read_text()

        scan_json_file = res.files(scan_data).joinpath("dummy_scan.json")
        cls.scan_str = scan_json_file.read_text()

    @pytest.fixture(autouse=True)
    def setup_function(
        self: TestSubarrayClient,
        device_clients_pkg: DeviceClientPkg,
        recording_pkg: RecordingPkg,
    ):
        """
        Setup a SubarrayClient for testing and correct registration for outer
        fixture subarray cleanup.
        """
        # Create subarray proxy, add to subarray_dict for potential cleanup,
        # and send to empty
        subarray_1_fqdn = gen_subarray_fqdn(1)
        device_clients_pkg.subarray_dict[subarray_1_fqdn] = SubarrayClient(
            subarray_1_fqdn, recording_pkg.alobserver
        )
        self.subarray_1 = device_clients_pkg.subarray_dict[subarray_1_fqdn]
        self.subarray_1.send_to_empty()

    def test_nominal_scan(self: TestSubarrayClient):
        """
        Test nominal scan sequence as defined in
        https://developer.skao.int/projects/ska-mid-cbf-mcs/en/latest/guide/interfaces/lmc_mcs_interface.html
        """
        # Test nominal scan sequence
        self.subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        self.subarray_1.configure_scan(self.conf_scan_str)
        self.subarray_1.scan(self.scan_str)
        self.subarray_1.end_scan()
        self.subarray_1.go_to_idle()
        self.subarray_1.remove_all_receptors()

    def test_removereceptors(
        self: TestSubarrayClient,
        recording_pkg: RecordingPkg,
    ):
        """
        Test obsreset maintains recetors and does not go to EMPTY but to IDLE.
        """
        # Add receptors
        self.subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        self.subarray_1.remove_receptors(["SKA001", "SKA036"])

        # Check some receptors removed in order invariant fashion and that
        # correctly got to and checked IDLE
        recording_pkg.alobserver.observe_equality(
            self.subarray_1.get_obsstate(), ObsState.IDLE
        )
        recording_pkg.alobserver.observe_equality(
            len(self.subarray_1.get_receptors()), len(["SKA063", "SKA100"])
        )
        recording_pkg.alobserver.observe_equality(
            set(self.subarray_1.get_receptors()), set(["SKA063", "SKA100"])
        )

        # Check remaining receptors removed
        self.subarray_1.remove_receptors(["SKA063", "SKA100"])
        recording_pkg.alobserver.observe_equality(
            self.subarray_1.get_obsstate(), ObsState.EMPTY
        )

    def test_obsreset(self: TestSubarrayClient, recording_pkg: RecordingPkg):
        """
        Test obsreset maintains recetors and does not go to EMPTY but to IDLE.
        """
        # Test obsreset doesn't go to empty
        receptors = ["SKA001", "SKA036", "SKA063", "SKA100"]
        self.subarray_1.add_receptors(receptors)
        self.subarray_1.abort()
        self.subarray_1.obsreset()
        recording_pkg.alobserver.observe_equality(
            self.subarray_1.get_obsstate(), ObsState.IDLE
        )

        # Check same receptors in order invariant fashion
        recording_pkg.alobserver.observe_equality(
            len(self.subarray_1.get_receptors()), len(receptors)
        )
        recording_pkg.alobserver.observe_equality(
            set(self.subarray_1.get_receptors()), set(receptors)
        )

    def test_send_to_empty(
        self: TestSubarrayClient,
        recording_pkg: RecordingPkg,
    ):
        """
        Test send to empty from all possible stable states in state machine of:
        https://developer.skao.int/projects/ska-control-model/en/latest/obs_state.html
        """
        receptors = ["SKA001", "SKA036", "SKA063", "SKA100"]

        # Test EMPTY from IDLE
        self.subarray_1.add_receptors(receptors)
        self.subarray_1.send_to_empty()
        recording_pkg.alobserver.observe_equality(
            self.subarray_1.get_obsstate(), ObsState.EMPTY
        )

        # Test EMPTY from READY
        self.subarray_1.add_receptors(receptors)
        self.subarray_1.configure_scan(self.conf_scan_str)
        self.subarray_1.send_to_empty()
        recording_pkg.alobserver.observe_equality(
            self.subarray_1.get_obsstate(), ObsState.EMPTY
        )

        # Test EMPTY from SCANNING
        self.subarray_1.add_receptors(receptors)
        self.subarray_1.configure_scan(self.conf_scan_str)
        self.subarray_1.scan(self.scan_str)
        self.subarray_1.send_to_empty()
        recording_pkg.alobserver.observe_equality(
            self.subarray_1.get_obsstate(), ObsState.EMPTY
        )

        # Test EMPTY from ABORTED
        self.subarray_1.add_receptors(receptors)
        self.subarray_1.abort()
        self.subarray_1.send_to_empty()
        recording_pkg.alobserver.observe_equality(
            self.subarray_1.get_obsstate(), ObsState.EMPTY
        )
