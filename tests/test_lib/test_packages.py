"""TODO"""
from __future__ import annotations

import dataclasses
import logging
from typing import Dict

from assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode,
)
from ska_tango_testing.integration import TangoEventTracer

from ska_mid_cbf_int_tests.mcs_command import ControllerClient, SubarrayClient


@dataclasses.dataclass
class RecordingPkg:
    """TODO"""

    logger: logging.Logger
    event_tracer: TangoEventTracer
    alobserver: AssertiveLoggingObserver

    def __init__(
        self: RecordingPkg,
        logger: logging.Logger,
        asserting_mode: AssertiveLoggingObserverMode,
    ):
        self.logger = logger
        self.event_tracer = TangoEventTracer()

        self.alobserver = AssertiveLoggingObserver(asserting_mode, self.logger)
        self.alobserver.set_event_tracer(self.event_tracer)

    def reset_tracer(self: RecordingPkg):
        """TODO"""
        self.event_tracer.unsubscribe_all()
        self.event_tracer.clear_events()


@dataclasses.dataclass
class DeviceClientPkg:
    """TODO"""

    controller: ControllerClient
    subarray_dict: Dict[str, SubarrayClient] = dataclasses.field(
        default_factory=dict
    )

    def prep_event_tracer(
        self: DeviceClientPkg, event_tracer: TangoEventTracer
    ):
        """TODO"""
        self.controller.prep_event_tracer(event_tracer)
