"""SubarrayClient testing."""

from __future__ import annotations

import json
import os

from ska_control_model import ObsState

from ska_mid_cbf_int_tests.cbf_command import SubarrayClient
from ska_mid_cbf_int_tests.constants.tango_constants import gen_subarray_fqdn

from ..test_lib.test_packages import DeviceClientPkg, RecordingPkg

SUBARRAY_CLIENT_TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestSubarrayClient:
    """Tests command sequencing and functionality of SubarrayClient."""

    @classmethod
    def setup_class(cls: TestSubarrayClient):
        """Read in dummy_configure_scan str and dummy_scan str."""
        with open(
            os.path.join(
                SUBARRAY_CLIENT_TEST_DATA_DIR, "dummy_configure_scan.json"
            ),
            "r",
            encoding="utf_8",
        ) as file_in:
            cls.conf_scan_str = json.dumps(json.load(file_in))

        with open(
            os.path.join(SUBARRAY_CLIENT_TEST_DATA_DIR, "dummy_scan.json"),
            "r",
            encoding="utf_8",
        ) as file_in:
            cls.scan_str = json.dumps(json.load(file_in))

    def test_nominal_scan(
        self: TestSubarrayClient,
        device_clients_pkg: DeviceClientPkg,
        recording_pkg: RecordingPkg,
    ):
        """
        Test nominal scan sequence as defined in
        https://developer.skao.int/projects/ska-mid-cbf-mcs/en/latest/guide/interfaces/lmc_mcs_interface.html
        """
        # Create subarray proxy, add to subarray_dict for potential cleanup,
        # and send to empty
        subarray_1_fqdn = gen_subarray_fqdn(1)
        device_clients_pkg.subarray_dict[subarray_1_fqdn] = SubarrayClient(
            subarray_1_fqdn, recording_pkg.alobserver
        )
        subarray_1 = device_clients_pkg.subarray_dict[subarray_1_fqdn]
        subarray_1.send_to_empty()

        # Test nominal scan sequence
        subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        subarray_1.configure_scan(self.conf_scan_str)
        subarray_1.scan(self.scan_str)
        subarray_1.end_scan()
        subarray_1.go_to_idle()
        subarray_1.remove_all_receptors()

    def test_reset(
        self: TestSubarrayClient,
        device_clients_pkg: DeviceClientPkg,
        recording_pkg: RecordingPkg,
    ):
        """Test reset maintains receptors."""
        # Create subarray proxy, add to subarray_dict for potential cleanup,
        # and send to empty
        subarray_1_fqdn = gen_subarray_fqdn(1)
        device_clients_pkg.subarray_dict[subarray_1_fqdn] = SubarrayClient(
            subarray_1_fqdn, recording_pkg.alobserver
        )
        subarray_1 = device_clients_pkg.subarray_dict[subarray_1_fqdn]
        subarray_1.send_to_empty()

        # Test reset doesn't go to empty
        subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        subarray_1.abort()
        subarray_1.reset()
        recording_pkg.alobserver.observe_equality(
            subarray_1.get_obsstate(), ObsState.IDLE
        )

    def test_send_to_empty(
        self: TestSubarrayClient,
        device_clients_pkg: DeviceClientPkg,
        recording_pkg: RecordingPkg,
    ):
        """
        Test send to empty from all possible stable states in state machine of:
        https://developer.skao.int/projects/ska-control-model/en/latest/obs_state.html
        """
        # Create subarray proxy, add to subarray_dict for potential cleanup,
        # and send to empty
        subarray_1_fqdn = gen_subarray_fqdn(1)
        device_clients_pkg.subarray_dict[subarray_1_fqdn] = SubarrayClient(
            subarray_1_fqdn, recording_pkg.alobserver
        )
        subarray_1 = device_clients_pkg.subarray_dict[subarray_1_fqdn]
        subarray_1.send_to_empty()

        # Test EMPTY from IDLE
        subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        subarray_1.send_to_empty()
        recording_pkg.alobserver.observe_equality(
            subarray_1.get_obsstate(), ObsState.EMPTY
        )

        # Test EMPTY from READY
        subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        subarray_1.configure_scan(self.conf_scan_str)
        subarray_1.send_to_empty()
        recording_pkg.alobserver.observe_equality(
            subarray_1.get_obsstate(), ObsState.EMPTY
        )

        # Test EMPTY from SCANNING
        subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        subarray_1.configure_scan(self.conf_scan_str)
        subarray_1.scan(self.scan_str)
        subarray_1.send_to_empty()
        recording_pkg.alobserver.observe_equality(
            subarray_1.get_obsstate(), ObsState.EMPTY
        )

        # Test EMPTY from ABORTED
        subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        subarray_1.abort()
        subarray_1.send_to_empty()
        recording_pkg.alobserver.observe_equality(
            subarray_1.get_obsstate(), ObsState.EMPTY
        )
