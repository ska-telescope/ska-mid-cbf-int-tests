"""TODO"""
import dataclasses
import logging
import os
from typing import Generator, Set

import pytest
from assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode,
)
from ska_tango_testing.integration import TangoEventTracer
from test_logging.format import LOG_FORMAT

from constants.tango_constants import CONTROLLER_FQDN
from mcs_command import ControllerClient, SubarrayClient


@dataclasses.dataclass
class RecordingPkg:
    """TODO"""

    logger: logging.Logger = None
    event_tracer: TangoEventTracer = None
    alobserver: AssertiveLoggingObserver = None


@pytest.fixture(scope="session")
def recording_pkg_sesh_setup(request) -> RecordingPkg:
    """TODO"""
    asserting = bool(int(request.config.getoption("--alo-asserting")))

    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    recording_pkg_obj = RecordingPkg(
        logging.getLogger(__name__), TangoEventTracer(), None
    )

    if asserting:
        recording_pkg_obj.logger.info("ALO Mode: ASSERTING")
        assertion_mode = AssertiveLoggingObserverMode.ASSERTING
    else:
        recording_pkg_obj.logger.info("ALO Mode: REPORTING")
        assertion_mode = AssertiveLoggingObserverMode.REPORTING

    recording_pkg_obj.alobserver = AssertiveLoggingObserver(
        assertion_mode, recording_pkg_obj.logger
    )
    recording_pkg_obj.alobserver.set_event_tracer(
        recording_pkg_obj.event_tracer
    )

    return recording_pkg_obj


@pytest.fixture()
def recording_pkg(
    recording_pkg_sesh_setup: RecordingPkg,
) -> Generator[RecordingPkg, None, None]:
    """TODO"""
    # Setup

    recording_pkg_obj = recording_pkg_sesh_setup

    yield recording_pkg_obj

    # Teardown

    # Clear event_tracer of subscriptions and events
    recording_pkg_obj.event_tracer.unsubscribe_all()
    recording_pkg_obj.event_tracer.clear_events()


@dataclasses.dataclass
class DeviceClientPkg:
    """TODO"""

    controller: ControllerClient = None
    subarray_set: Set[SubarrayClient] = dataclasses.field(default_factory=set)


@pytest.fixture(scope="session")
def device_clients_pkg_sesh_setup_teardown(
    request,
    recording_pkg_sesh_setup,
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

    device_clients_pkg_obj = DeviceClientPkg(
        ControllerClient(CONTROLLER_FQDN, recording_pkg_sesh_setup.alobserver),
        set(),
    )
    device_clients_pkg_obj.controller.admin_mode_online()
    device_clients_pkg_obj.controller.simulation_mode_on()

    yield device_clients_pkg_obj

    # Teardown

    device_clients_pkg_obj.controller.admin_mode_offline()


@pytest.fixture()
def device_clients_pkg(
    device_clients_pkg_sesh_setup_teardown,
) -> Generator[DeviceClientPkg, None, None]:
    """TODO"""
    # Setup

    # Return device_clients_pkg_obj
    device_clients_pkg_obj = device_clients_pkg_sesh_setup_teardown

    yield device_clients_pkg_obj

    # Teardown

    # Clear subarray_set and return all to empty
    while len(device_clients_pkg_obj.subarray_set) != 0:
        subarray_client = device_clients_pkg_obj.subarray_set.pop()
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
