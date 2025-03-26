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

import ska_mid_cbf_int_tests.cbf_data.configure_scan as configure_scan_data
import ska_mid_cbf_int_tests.cbf_data.init_sys_param as init_sys_param_data
import ska_mid_cbf_int_tests.cbf_data.scan as scan_data


@dataclasses.dataclass
class CommonNotebookPkg:
    # pylint: disable=too-many-instance-attributes
    """TODO"""

    # Tango host information
    kube_namespace: str
    tango_host: str
    cluster_domain: str

    # CBF control information
    deployer_json: List[str]
    init_sys_param: str

    # Scan information
    subarray_no: int
    receptors: List[str]
    scan_config: str
    scan: str

    # Recording class instances
    alobserver: AssertiveLoggingObserver
    logger: logging.Logger

    def __init__(self: CommonNotebookPkg, param_json_path: str):

        with open(param_json_path, "r", encoding="utf-8") as json_in:
            param_json = json.load(json_in)

        tango_host_connection_json = param_json["tango_host_connection"]
        self.namespace_tango_db_address = tango_host_connection_json[
            "namespace_tango_db_address"
        ]
        self.kube_namespace = tango_host_connection_json["kube_namespace"]
        self.kube_cluster_domain = tango_host_connection_json[
            "kube_cluster_domain"
        ]

        deployer_json = param_json["deployer"]
        self.deployer_talons = deployer_json["talons"]

        controller_json = param_json["controller"]
        self.init_sys_param = (
            importlib.resources.files(init_sys_param_data)
            .joinpath(controller_json["init_sys_param_id"] + ".json")
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

        scan_json = param_json["scan"]
        self.subarray_no = scan_json["subarray_no"]
        self.receptors = scan_json["receptors"]
        self.scan_config = (
            importlib.resources.files(configure_scan_data)
            .joinpath(scan_json["scan_config_id"] + ".json")
            .read_text()
        )
        self.scan = (
            importlib.resources.files(scan_data)
            .joinpath(scan_json["scan_id"] + ".json")
            .read_text()
        )
