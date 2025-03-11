"""Functions to wait for conditions to be satisfied."""

import time

import pytest

TIMEOUT = 60.0
INTERVAL = 0.5


def wait_for_predicate(
    predicate, description, timeout=TIMEOUT, interval=INTERVAL
):
    """
    Wait for predicate to be true.

    :param predicate: callable to test
    :param description: description to use if test fails
    :param timeout: timeout in seconds
    :param interval: interval between tests of the predicate in seconds

    """
    start = time.time()
    while True:
        if predicate():
            break
        if time.time() >= start + timeout:
            pytest.fail(f"{description} not achieved after {timeout} seconds")
        time.sleep(interval)


def wait_for_state(device, state, timeout=TIMEOUT):
    """
    Wait for device state to have the expected value.

    :param device: device client
    :param state: the expected state
    :param timeout: timeout in seconds

    """

    def predicate():
        return device.get_attribute("State") == state

    description = f"Device state {state}"
    wait_for_predicate(predicate, description, timeout=timeout)
