"""
Nominal scan sequence.
"""
from __future__ import annotations

import json
import os

from ska_mid_cbf_int_tests.constants.tango_constants import gen_subarray_fqdn
from ska_mid_cbf_int_tests.mcs_command import SubarrayClient

M3_DATA_DIR = "m3/data"


class TestNominalScan:

    @classmethod
    def setup(cls: TestNominalScan):

        with open(
            os.path.join(M3_DATA_DIR, "dummy_configure_scan.json"), "r"
        ) as f:
            cls.conf_scan_str = json.dumps(json.load(f)).replace("\n", "")

        with open(
            os.path.join(M3_DATA_DIR, "dummy_init_sys_param.json"), "r"
        ) as f:
            cls.init_sys_str = json.dumps(json.load(f)).replace("\n", "")

        with open(
            os.path.join(M3_DATA_DIR, "dummy_scan.json"), "r"
        ) as f:
            cls.scan_str = json.dumps(json.load(f)).replace("\n", "")

    def test_scan(
        self: TestNominalScan,
        # device_client_pkg: DeviceClientPkg,
        recording_pkg: RecordingPkg
    ):
        """Test nominal scan sequence."""
        # subarray_1_fqdn = gen_subarray_fqdn(1)
        # device_client_pkg.subarray_dict[subarray_1_fqdn] = SubarrayClient(
        #     subarray_1_fqdn
        # )

        # device_client_pkg.subarray_dict[subarray_1_fqdn].

    def test_scan_2(recording_pkg):
        """Test nominal scan sequence 2."""
        recording_pkg.alobserver.observe_true(False)
