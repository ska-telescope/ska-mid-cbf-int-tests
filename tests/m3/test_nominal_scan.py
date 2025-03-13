"""
Nominal scan sequence.
"""
from __future__ import annotations

import json
import os

from ska_mid_cbf_int_tests.cbf_command import SubarrayClient
from ska_mid_cbf_int_tests.constants.tango_constants import gen_subarray_fqdn

from ..test_lib.test_packages import DeviceClientPkg, RecordingPkg

M3_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestNominalScan:
    """TODO"""

    @classmethod
    def setup_class(cls: TestNominalScan):
        """TODO"""
        with open(
            os.path.join(M3_DATA_DIR, "dummy_configure_scan.json"),
            "r",
            encoding="utf_8",
        ) as file_in:
            cls.conf_scan_str = json.dumps(json.load(file_in)).replace(
                "\n", ""
            )

        with open(
            os.path.join(M3_DATA_DIR, "dummy_scan.json"), "r", encoding="utf_8"
        ) as file_in:
            cls.scan_str = json.dumps(json.load(file_in)).replace("\n", "")

    def test_scan(
        self: TestNominalScan,
        device_clients_pkg: DeviceClientPkg,
        recording_pkg: RecordingPkg,
    ):
        """Test nominal scan sequence."""
        # Create subarray proxy and add to subarray_dict for potential cleanup
        subarray_1_fqdn = gen_subarray_fqdn(1)
        device_clients_pkg.subarray_dict[subarray_1_fqdn] = SubarrayClient(
            subarray_1_fqdn, recording_pkg.alobserver
        )

        subarray_1 = device_clients_pkg.subarray_dict[subarray_1_fqdn]
        subarray_1.prep_event_tracer(recording_pkg.event_tracer)
        subarray_1.send_to_empty()

        recording_pkg.logger.info("Starting LMC to MCS Subarray Scan Sequence")

        subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        subarray_1.configure_scan(self.conf_scan_str)
        subarray_1.scan(self.scan_str)
        subarray_1.end_scan()
        subarray_1.go_to_idle()
        subarray_1.remove_all_receptors()

    def test_scan_2(
        self: TestNominalScan,
        device_clients_pkg: DeviceClientPkg,
        recording_pkg: RecordingPkg,
    ):
        """Test nominal scan sequence 2."""
        # Create subarray proxy and add to subarray_dict for potential cleanup
        subarray_1_fqdn = gen_subarray_fqdn(1)
        device_clients_pkg.subarray_dict[subarray_1_fqdn] = SubarrayClient(
            subarray_1_fqdn, recording_pkg.alobserver
        )

        subarray_1 = device_clients_pkg.subarray_dict[subarray_1_fqdn]
        subarray_1.prep_event_tracer(recording_pkg.event_tracer)
        subarray_1.send_to_empty()

        recording_pkg.logger.info("Starting LMC to MCS Subarray Scan Sequence")

        subarray_1.add_receptors(["SKA001", "SKA036", "SKA063", "SKA100"])
        subarray_1.configure_scan(self.conf_scan_str)
        subarray_1.scan(self.scan_str)
        subarray_1.end_scan()
        subarray_1.go_to_idle()
        subarray_1.remove_all_receptors()
