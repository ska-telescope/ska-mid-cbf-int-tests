import logging

from assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode
)
from test_logging.format import LOG_FORMAT

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
test_logger = logging.getLogger(__name__)

def test_scan():
    alobserver = AssertiveLoggingObserver(
        AssertiveLoggingObserverMode.ASSERTING,
        test_logger
    )
    alobserver.observe_true(False)
