"""
Conftest containing pytest configuration for cbf_command basic client testing.
"""

import json
import os
from typing import Generator

import pytest

from ska_mid_cbf_int_tests.cbf_command import DeployerClient
from ska_mid_cbf_int_tests.constants.tango_constants import DEPLOYER_FQDN

from ..test_lib.test_packages import DeviceClientPkg

CBF_COMMAND_TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture(scope="package", autouse=True)
def cbf_command_test_setup_teardown(
    device_clients_pkg_sesh_setup_teardown,
) -> Generator[DeviceClientPkg, None, None]:
    """
    Pytest Fixture setting up and tearing down the session DeviceClientPkg
    instance for the cbf_command testing package. Turns CBF on in simulation
    mode using current sequence descibed in "Notes". Ensures admin mode is
    online and in event of error fatal to session that admin mode is set to
    offline before propagating the error.

    Notes:
    - TEMP: Uses EC deployer interacting with TDC attributes and commands,
    will be used until replaced or changed in AA2+
    - TEMP: Turns CBF on using similar sequence to minimal controller
    integration tests of https://gitlab.com/ska-telescope/ska-mid-cbf-mcs will
    change sequence once MCS is changed for AA2+

    :param device_clients_pkg_sesh_setup_teardown: Dependency fixture
        setting up and returning the session's DeviceClientPkg instance
    :return: pytest session's DeviceClientPkg instance
    """
    # Setup
    device_clients_pkg_obj = device_clients_pkg_sesh_setup_teardown

    # TEMP: Use deployer to write target talons and generate config json for
    # controller
    deployer_client = DeployerClient(DEPLOYER_FQDN)
    deployer_client.wr_target_talons([1, 2, 3, 4])
    deployer_client.generate_config_jsons()

    # Note: will break if simulationMode is added to deployment as is planned
    #       so remove if that happens and adjust accordingly, just here to
    #       explicitly remind us that simulation mode is TRUE
    device_clients_pkg_obj.controller.simulation_mode_on()

    # CBF Controller On Sequence Start

    # If anything goes wrong with session in scope of admin mode online ensure
    # admin mode is set to offline after
    device_clients_pkg_obj.controller.admin_mode_online()
    try:
        with open(
            os.path.join(
                CBF_COMMAND_TEST_DATA_DIR, "dummy_init_sys_param.json"
            ),
            "r",
            encoding="utf_8",
        ) as file_in:
            device_clients_pkg_obj.controller.init_sys_param(
                json.dumps(json.load(file_in))
            )
        device_clients_pkg_obj.controller.on()

        yield device_clients_pkg_obj

        # Teardown

        device_clients_pkg_obj.controller.admin_mode_offline()

    except Exception as exception:
        device_clients_pkg_obj.controller.admin_mode_offline()
        raise exception
