"""
Module containing test relevant class instance packages to reduce the number of
fixtures necessary for testing and improve organization/readability.
"""
from __future__ import annotations

import dataclasses
import logging
from typing import Dict

from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode,
)

from ska_mid_cbf_int_tests.cbf_command import ControllerClient, SubarrayClient


@dataclasses.dataclass
class RecordingPkg:
    """
    Package for testing grouping class instances relevant to recording.
    """

    logger: logging.Logger
    alobserver: AssertiveLoggingObserver

    def __init__(
        self: RecordingPkg,
        logger: logging.Logger,
        asserting_mode: AssertiveLoggingObserverMode,
    ):
        self.logger = logger
        self.alobserver = AssertiveLoggingObserver(asserting_mode, self.logger)


@dataclasses.dataclass
class DeviceClientPkg:
    """
    Package for testing grouping class instances of relevant device clients.
    """

    controller: ControllerClient
    subarray_dict: Dict[str, SubarrayClient] = dataclasses.field(
        default_factory=dict
    )
