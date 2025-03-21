"""TODO"""

from __future__ import annotations

import dataclasses
import importlib.resources
import json
import logging
from typing import List

from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode,
)
from ska_mid_cbf_common_test_infrastructure.test_logging.format import (
    LOG_FORMAT,
)

import ska_mid_cbf_int_tests.data.configure_scan as configure_scan_data
import ska_mid_cbf_int_tests.data.init_sys_param as init_sys_param_data
import ska_mid_cbf_int_tests.data.scan as scan_data


@dataclasses.dataclass
class CommonNotebookPkg:
    """TODO"""
    # Scan parameters
    deployer_json: List[str]
    init_sys_param: str
    configure_scan: str
    scan: str

    # Recording class instances
    alobserver: AssertiveLoggingObserver
    logger: logging.Logger

    def __init__(self: CommonNotebookPkg, param_json_path: str):

        param_json = json.load(open(param_json_path))

        deployer_json = param_json["deployer"]
        self.deployer_talons = deployer_json["talons"]

        controller_json = param_json["controller"]
        self.init_sys_param = (
            importlib.resources.files(init_sys_param_data)
            .joinpath(controller_json["init_sys_param_id"] + ".json")
            .read_text()
        )
        self.configure_scan = (
            importlib.resources.files(configure_scan_data)
            .joinpath(controller_json["configure_scan_id"] + ".json")
            .read_text()
        )
        self.scan = (
            importlib.resources.files(scan_data)
            .joinpath(controller_json["scan_id"] + ".json")
            .read_text()
        )

        recording_json = param_json["recording"]
        logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.alobserver = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.ASSERTING
            if recording_json["asserting"]
            else AssertiveLoggingObserverMode.REPORTING,
            self.logger,
        )
