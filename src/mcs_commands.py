from typing import List

from tango import DeviceProxy

from assertive_logging_observer import AssertiveLoggingObserver

from timeout_constants import (
    TIMEOUT_SHORT,
    TIMEOUT_MEDIUM,
    TIMEOUT_LONG
)

def subarray_add_receptors(
    subarray_proxy: DeviceProxy,
    receptors: List[int],
    alobserver: AssertiveLoggingObserver
):
    
    alobserver.logger.info(f"Adding receptors {receptors}")

    lrc_result = subarray_proxy.command_read_write("AddReceptors", receptors)

    alobserver.()
