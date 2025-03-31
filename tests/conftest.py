"""
Conftest containing general pytest configuration for all ska-mid-cbf-int-tests
basic client and integration milestone tests.
"""

import logging
from typing import Generator

import pytest
from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserverMode,
)
from ska_mid_cbf_common_test_infrastructure.test_logging.format import (
    LOG_FORMAT,
)

from ska_mid_cbf_int_tests.cbf_command import ControllerClient
from ska_mid_cbf_int_tests.cbf_constants.tango_constants import CONTROLLER_FQDN
from ska_mid_cbf_int_tests.env_management.connect_tango_host import (
    connect_tango_host,
)

from .test_lib.test_packages import DeviceClientPkg, RecordingPkg


@pytest.fixture(scope="session")
def call_connect_tango_host(request: pytest.FixtureRequest):
    """Pytest Fixture for connecting to TANGO_HOST for session."""
    kube_namespace = request.config.getoption("--kube-namespace")
    namespace_tango_db_address = request.config.getoption(
        "--namespace-tango-db-address"
    )
    kube_cluster_domain = request.config.getoption("--kube-cluster-domain")
    connect_tango_host(
        namespace_tango_db_address, kube_namespace, kube_cluster_domain
    )


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
    call_connect_tango_host,
    recording_pkg: RecordingPkg,
) -> Generator[DeviceClientPkg, None, None]:
    """
    Pytest Fixture setting up and tearing down the main DeviceClientPkg class
    instance of the pytest session. Leaves actual device setup and teardown
    to the conftest of each test package but instantiates Controller since
    will be used across all tests.

    :param connect_tango_host: Dependency fixture
    :param recording_pkg: Dependency fixture of RecordingPkg for pytest
        session, used to associate alobserver to instantiated device client
        instances
    :return: pytest session's DeviceClientPkg instance
    """

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

    :param device_clients_pkg_sesh_setup_teardown: Dependency fixture
        setting up and returning the session's DeviceClientPkg instance
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
    call_connect_tango_host,
    recording_pkg,
    device_clients_pkg_sesh_setup_teardown,
):
    """
    General pytest session setup and teardown, used to ensure pytest
    session is connected to TANGO_HOST and that the session's RecordingPkg and
    DeviceClientPkg are instantiated.
    """
    # Setup
    yield
    # Teardown


def pytest_addoption(parser):  # pylint: disable=C0116

    parser.addoption("--namespace-tango-db-address", action="store")
    parser.addoption("--kube-namespace", action="store")
    parser.addoption("--kube-cluster-domain", action="store")

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
