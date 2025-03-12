"""TODO"""
import dataclasses
import logging
from typing import Dict

from assertive_logging_observer import AssertiveLoggingObserver
from ska_tango_testing.integration import TangoEventTracer

from ska_mid_cbf_int_tests.mcs_command import ControllerClient, SubarrayClient


@dataclasses.dataclass
class RecordingPkg:
    """TODO"""

    logger: logging.Logger = None
    event_tracer: TangoEventTracer = None
    alobserver: AssertiveLoggingObserver = None


@dataclasses.dataclass
class DeviceClientPkg:
    """TODO"""

    controller: ControllerClient = None
    subarray_dict: Dict[str, SubarrayClient] = dataclasses.field(
        default_factory=dict
    )
