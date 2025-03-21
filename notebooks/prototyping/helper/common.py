"""TODO"""

import logging

from ska_mid_cbf_common_test_infrastructure.assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode,
)
from ska_mid_cbf_common_test_infrastructure.test_logging.format import (
    LOG_FORMAT,
)

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
test_logger = logging.getLogger(__name__)

# import os

# from notebook_parameters import NotebookParameters


def it_notebook_common_setup() -> AssertiveLoggingObserver:
    """TODO"""
    return AssertiveLoggingObserver(test_logger, AssertiveLoggingObserverMode)
