"""
Module containing general pytest configuration for ska-mid-cbf-int-tests
milestone tests.
"""
import json
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

from ska_mid_cbf_int_tests.cbf_command import ControllerClient, DeployerClient
from ska_mid_cbf_int_tests.constants.tango_constants import (
    CONTROLLER_FQDN,
    DEPLOYER_FQDN,
)

from .test_lib.test_packages import DeviceClientPkg, RecordingPkg

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


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
    request: pytest.FixtureRequest,
    recording_pkg: RecordingPkg,
) -> Generator[DeviceClientPkg, None, None]:
    """
    Pytest Fixture setting up and tearing down the main DeviceClientPkg class
    instance of the pytest session. Turns CBF on instantiating ControllerClient
    and using current sequence with its context descibed in "Notes". Ensures
    admin mode is online and in event of error fatal to session that admin mode
    is set to offline before propagating the error.

    Notes:
    - TEMP: Uses EC deployer interacting with TDC attributes and commands,
    will be used until replaced or changed in AA2+
    - TEMP: Sets to simulation mode on until bitstream + FHS + MCS connection
    is defined and completed
    - TEMP: Turns CBF on using similar sequence to minimal controller
    integration tests of https://gitlab.com/ska-telescope/ska-mid-cbf-mcs will
    change sequence once MCS is changed for AA2+

    :param recording_pkg: Fixture of RecordingPkg for pytest session, used to
        associate alobserver to instantiated device client instances
    :return: pytest session's DeviceClientPkg instance
    """
    # Setup

    # Connect to TANGO_HOST
    tango_host = request.config.getoption("--tango-host")
    namespace = request.config.getoption("--namespace")
    cluster_domain = request.config.getoption("--cluster-domain")
    tango_hostname, tango_port = tango_host.split(":")
    os.environ[
        "TANGO_HOST"
    ] = f"{tango_hostname}.{namespace}.svc.{cluster_domain}:{tango_port}"

    # TEMP: Use deployer to write target talons and generate config json for
    # controller
    deployer_client = DeployerClient(DEPLOYER_FQDN, 250)
    deployer_client.wr_target_talons([1, 2, 3, 4])
    deployer_client.generate_config_jsons()

    device_clients_pkg_obj = DeviceClientPkg(
        ControllerClient(CONTROLLER_FQDN, recording_pkg.alobserver),
        {},
    )

    # TEMP: Set to simulation mode off, use until MCS-FHS connection is ready
    # Note: will break if simulationMode is added to deployment as is planned
    #       so remove if that happens, just here to explicitly remind us that
    #       simulation mode is TRUE
    device_clients_pkg_obj.controller.simulation_mode_on()

    # CBF Controller On Sequence Start

    # If anything goes wrong with session in scope of admin mode online ensure
    # admin mode is set to offline after
    device_clients_pkg_obj.controller.admin_mode_online()
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
) -> Generator[DeviceClientPkg, None, None]:
    """
    Wrapper class used to retrieve Pytest Fixture for the main DeviceClientPkg
    class instance of the pytest session. On each call ensures teardown of any
    subarrays added to main DeviceClientPkg's subarray_dict.

    :param device_clients_pkg_sesh_setup_teardown: Resulting DeviceClientPkg
        for pytest session from setup
    :return: pytest session's RecordingPkg instance
    """
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
    recording_pkg, device_clients_pkg_sesh_setup_teardown
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
