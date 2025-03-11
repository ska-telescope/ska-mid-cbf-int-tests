"""TODO"""
import dataclasses
import logging
from typing import Generator, Set

import pytest
from assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode,
)
from ska_tango_testing.integration import TangoEventTracer
from test_logging.format import LOG_FORMAT

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
    asserting = bool(request.config.getoption("--asserting"))
    if asserting:
        assertion_mode = AssertiveLoggingObserverMode.ASSERTING
    else:
        assertion_mode = AssertiveLoggingObserverMode.REPORTING

    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    recording_pkg_obj = RecordingPkg()

    recording_pkg_obj.logger = logging.getLogger(__name__)
    recording_pkg_obj.event_tracer = TangoEventTracer()

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
    recording_pkg_obj = recording_pkg_sesh_setup

    yield recording_pkg_obj

    # Teardown clear event_tracer of subscriptions and events
    recording_pkg_obj.event_tracer.unsubscribe_all()
    recording_pkg_obj.event_tracer.clear_events()


@dataclasses.dataclass
class DeviceClientPkg:
    """TODO"""

    controller: ControllerClient = None
    subarray_set: Set[SubarrayClient] = dataclasses.field(default_factory=set)


# @pytest.fixture(scope="session")
# def device_clients_pkg_sesh_setup(alobserver) -> DeviceClientPkg:

#     CONTROLLER_FQDN = "mid_csp_cbf/sub_elt/controller"

#     return DeviceClientTuple(
#         ControllerClient(CONTROLLER_FQDN, alobserver),
#         set()
#     )


# @pytest.fixture()
# def device_clients_pkg(
#     device_clients_pkg_sesh_setup
# ) -> Generator[DeviceClientPkg, None, None]:

#     # Setup return device_clients_pkg_obj
#     device_clients_pkg_obj = device_clients_pkg_sesh_setup

#     yield device_clients_pkg_obj

#     # Teardown clear subarray_set and return all to empty
#     while len(device_clients_pkg_obj.subarray_set) != 0:
#         subarray_client = device_clients_pkg_obj.subarray_set.pop()
#         subarray_client.send_to_empty()


@pytest.fixture(scope="session")
def device_clients_pkg_sesh_setup(recording_pkg_sesh_setup):
    """TODO"""
    recording_pkg_sesh_setup.logger.info("Do Nothing")


@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown(
    recording_pkg_sesh_setup, device_clients_pkg_sesh_setup
):
    """TODO"""
    yield


def pytest_addoption(parser):  # pylint: disable=C0116
    parser.addoption(
        "--asserting",
        action="store",
        help=(
            "Whether to use AssertiveLoggingObserver in ASSERTING (1) or "
            "REPORTING (0)"
        ),
    )
