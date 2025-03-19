"""
Module containing general pytest configuration for ska-mid-cbf-int-tests
milestone tests.
"""
import logging
import os
from typing import Generator

import pytest
from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserverMode,
)
from ska_mid_cbf_common_test_infrastructure.test_logging.format import (
    LOG_FORMAT,
)

from ska_mid_cbf_int_tests.cbf_command import ControllerClient
from ska_mid_cbf_int_tests.constants.tango_constants import CONTROLLER_FQDN

from .test_lib.test_packages import DeviceClientPkg, RecordingPkg


@pytest.fixture(scope="session")
def connect_tango_host(request: pytest.FixtureRequest):
    """Pytest Ficture for connecting to TANGO_HOST for session"""
    tango_host = request.config.getoption("--tango-host")
    namespace = request.config.getoption("--namespace")
    cluster_domain = request.config.getoption("--cluster-domain")
    tango_hostname, tango_port = tango_host.split(":")
    os.environ[
        "TANGO_HOST"
    ] = f"{tango_hostname}.{namespace}.svc.{cluster_domain}:{tango_port}"


@pytest.fixture(scope="session")
def recording_pkg(request: pytest.FixtureRequest) -> RecordingPkg:
    """
    Pytest Fixture for the main RecordingPkg class instance of the pytest
    session. Aside from basic instantiation sets up AssertiveLoggingObserver
    (ALO) of RecordingPkg in given mode of --alo-asserting.

    :return: pytest session's RecordingPkg instance
    """
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    test_logger = logging.getLogger(__name__)

    asserting = bool(int(request.config.getoption("--alo-asserting")))
    if asserting:
        asserting_mode = AssertiveLoggingObserverMode.ASSERTING
    else:
        asserting_mode = AssertiveLoggingObserverMode.REPORTING

    recording_pkg = RecordingPkg(test_logger, asserting_mode)

    return recording_pkg


@pytest.fixture(scope="session")
def device_clients_pkg_sesh_setup_teardown(
    connect_tango_host,
    recording_pkg: RecordingPkg,
) -> Generator[DeviceClientPkg, None, None]:
    """TODO"""

    # Setup

    # Create and yield device_clients_pkg
    device_clients_pkg_obj = DeviceClientPkg(
        ControllerClient(CONTROLLER_FQDN, recording_pkg.alobserver),
        {},
    )

    yield device_clients_pkg_obj

    # Teardown


@pytest.fixture()
def device_clients_pkg(
    device_clients_pkg_sesh_setup_teardown: DeviceClientPkg,
) -> Generator[DeviceClientPkg, None, None]:
    """
    Wrapper class used to retrieve Pytest Fixture for the main DeviceClientPkg
    class instance of the pytest session. On each call ensures teardown of any
    subarrays added to main DeviceClientPkg's subarray_dict.

    :param device_clients_pkg_sesh_setup_teardown: Resulting DeviceClientPkg
        for pytest session from setup
    :return: pytest session's DeviceClientPkg instance
    """
    # Setup

    # Yield sesh DeviceClientPkg
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
    connect_tango_host, recording_pkg, device_clients_pkg_sesh_setup_teardown
):
    """
    General pytest session setup and teardown, used to ensure pytest
    session's RecordingPkg and DeviceClientPkg are instantiated.
    """
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
