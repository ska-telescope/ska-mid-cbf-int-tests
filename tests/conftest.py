"""TODO"""
import json
import logging
import os
from typing import Generator

import pytest
import tango
from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserverMode,
)
from ska_mid_cbf_common_test_infrastructure.test_logging.format import (
    LOG_FORMAT,
)

from ska_mid_cbf_int_tests.cbf_command import ControllerClient
from ska_mid_cbf_int_tests.constants.tango_constants import (
    CONTROLLER_FQDN,
    DEPLOYER_FQDN,
)

from .test_lib.test_packages import DeviceClientPkg, RecordingPkg

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture(scope="session")
def recording_pkg_sesh_setup(request: pytest.FixtureRequest) -> RecordingPkg:
    """TODO"""
    asserting = bool(int(request.config.getoption("--alo-asserting")))

    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    test_logger = logging.getLogger(__name__)

    if asserting:
        asserting_mode = AssertiveLoggingObserverMode.ASSERTING
    else:
        asserting_mode = AssertiveLoggingObserverMode.REPORTING

    recording_pkg = RecordingPkg(test_logger, asserting_mode)

    return recording_pkg


@pytest.fixture()
def recording_pkg(
    recording_pkg_sesh_setup: RecordingPkg,
) -> Generator[RecordingPkg, None, None]:
    """TODO"""
    # Setup

    recording_pkg_obj = recording_pkg_sesh_setup

    yield recording_pkg_obj

    # Teardown


@pytest.fixture(scope="session")
def device_clients_pkg_sesh_setup_teardown(
    request: pytest.FixtureRequest,
    recording_pkg_sesh_setup: RecordingPkg,
) -> Generator[DeviceClientPkg, None, None]:
    """TODO"""
    # Setup

    # Connect to TANGO_HOST
    tango_host = request.config.getoption("--tango-host")
    namespace = request.config.getoption("--namespace")
    cluster_domain = request.config.getoption("--cluster-domain")
    tango_hostname, tango_port = tango_host.split(":")
    os.environ[
        "TANGO_HOST"
    ] = f"{tango_hostname}.{namespace}.svc.{cluster_domain}:{tango_port}"

    # Temporary deployer
    deployer_proxy = tango.DeviceProxy(DEPLOYER_FQDN)
    deployer_proxy.set_timeout_millis(250000)
    deployer_proxy.write_attribute("targetTalons", [1, 2, 3, 4])
    deployer_proxy.command_inout("generate_config_jsons")

    device_clients_pkg_obj = DeviceClientPkg(
        ControllerClient(CONTROLLER_FQDN, recording_pkg_sesh_setup.alobserver),
        {},
    )

    # CBF Controller On Sequence
    device_clients_pkg_obj.controller.admin_mode_online()

    # If anything goes wrong with session in scope of controller
    # turn on ensure admin is off after
    try:
        with open(
            os.path.join(TEST_DATA_DIR, "dummy_init_sys_param.json"),
            "r",
            encoding="utf_8",
        ) as file_in:
            device_clients_pkg_obj.controller.init_sys_param(
                json.dumps(json.load(file_in)).replace("\n", "")
            )
        device_clients_pkg_obj.controller.on()

        yield device_clients_pkg_obj

        # Teardown

        device_clients_pkg_obj.controller.admin_mode_offline()

    except Exception as exception:
        device_clients_pkg_obj.controller.admin_mode_offline()
        raise exception


@pytest.fixture()
def device_clients_pkg(
    device_clients_pkg_sesh_setup_teardown: DeviceClientPkg,
    recording_pkg: RecordingPkg,
) -> Generator[DeviceClientPkg, None, None]:
    """TODO"""
    # Setup

    # Return device_clients_pkg_obj
    device_clients_pkg_obj = device_clients_pkg_sesh_setup_teardown

    yield device_clients_pkg_obj

    # Teardown

    # Clear subarray_dict returning all to empty, list to ensure soft copy
    # of keys to avoid dictionary changed size during iteration error
    for subarray_key in list(device_clients_pkg_obj.subarray_dict.keys()):
        subarray_client = device_clients_pkg_obj.subarray_dict.pop(
            subarray_key
        )
        subarray_client.send_to_empty()


@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown(
    recording_pkg_sesh_setup, device_clients_pkg_sesh_setup_teardown
):
    """TODO"""
    # Setup
    yield
    # Teardown


def pytest_addoption(parser):  # pylint: disable=C0116

    parser.addoption("--cluster-domain", action="store", help="Cluster domain")
    parser.addoption(
        "--namespace", action="store", help="Kubernetes namespace"
    )
    parser.addoption("--tango-host", action="store", help="Tango Host")

    parser.addoption(
        "--alo-asserting",
        action="store",
        help=(
            "Whether to use AssertiveLoggingObserver in ASSERTING (1) or "
            "REPORTING (0)"
        ),
        choices=(0, 1),
        type=int,
    )
