"""Subarray device tests."""

import json
import os
import random
from datetime import date

from common import TIMEOUT, tango_client, wait_for_predicate

TIMEOUT_ASSIGNRES = 120.0

# Translations for the obsState attribute. The Tango clients return an integer
# value, so this is used to convert the value into a name.
TRANSLATIONS = {
    "obsState": {
        0: "EMPTY",
        1: "RESOURCING",
        2: "IDLE",
        3: "CONFIGURING",
        4: "READY",
        5: "SCANNING",
        6: "ABORTING",
        7: "ABORTED",
        8: "RESETTING",
        9: "FAULT",
        10: "RESTARTING",
    }
}


# -------------------
# Ancillary functions
# -------------------

def call_command(subarray_device, command):
    """
    Call a device command.

    :param subarray_device: SDP subarray device client
    :param command: name of command to call

    """
    # Check command is present
    assert command in subarray_device.get_commands()
    # Get the command argument
    if command in [
        "AssignResources",
        "ReleaseResources",
        "Configure",
        "Scan",
    ]:
        config = read_command_argument(command)
        argument = json.dumps(config)
    else:
        argument = None

    # Remember the EB ID
    if command == "AssignResources":
        subarray_device.eb_id = config["execution_block"]["eb_id"]
    elif command == "End":
        subarray_device.eb_id = None

    # Call the command
    subarray_device.execute_command(command, argument=argument)


def read_command_argument(name):
    """
    Read command argument from JSON file.

    :param name: name of command

    """
    config = read_json_data(f"command_{name}.json")

    if name == "AssignResources":
        # Insert new IDs into configuration
        config["execution_block"]["eb_id"] = create_id("eb")
        for pblock in config["processing_blocks"]:
            pblock["pb_id"] = create_id("pb")

    return config


def create_id(prefix):
    """
    Create an ID with the given prefix.

    The ID will contain today's date and a random 5-digit number.

    :param prefix: the prefix

    """
    generator = "test"
    today = date.today().strftime("%Y%m%d")
    number = random.randint(0, 99999)
    return f"{prefix}-{generator}-{today}-{number:05d}"


def read_receive_addresses():
    """Read receive addresses from JSON file."""
    return read_json_data("receive_addresses.json")


def read_json_data(filename):
    """
    Read data from JSON file in the data directory.

    :param filename: name of the file to read

    """
    path = os.path.join("resources", filename)
    with open(path, "r", encoding="utf-8") as file_n:
        data = json.load(file_n)
    return data


def transition_commands(current, target):
    """
    Get list of commands to transition from current state to target state.

    :param current: tuple of current state and obs_state
    :param target: tuple of target state and obs_state
    :returns: list of commands

    """
    # Mapping of state and obs_state to state number
    state_number = {
        ("OFF", "EMPTY"): 0,
        ("ON", "EMPTY"): 1,
        ("ON", "IDLE"): 2,
        ("ON", "READY"): 3,
        ("ON", "SCANNING"): 4,
    }
    # Command to transition to previous state number
    command_prev = [None, "Off", "ReleaseResources", "End", "EndScan"]
    # Command to transition to next state number
    command_next = ["On", "AssignResources", "Configure", "Scan", None]

    current_number = state_number[current]
    target_number = state_number[target]

    if target_number < current_number:
        commands = [
            command_prev[i] for i in range(current_number, target_number, -1)
        ]
    elif target_number > current_number:
        commands = [
            command_next[i] for i in range(current_number, target_number)
        ]
    else:
        commands = []

    return commands


def set_state_and_obs_state(device, state, obs_state):
    """
    Set subarray device state and observing state.

    :param device: subarray device proxy
    :param state: the desired device state
    :param obs_state: the desired observing state

    """
    current = (
        device.get_attribute("State"),
        device.get_attribute("obsState"),
    )
    target = (state, obs_state)
    commands = transition_commands(current, target)

    for command in commands:
        call_command(device, command)
        if command == "AssignResources":
            wait_for_obs_state(device, "IDLE", timeout=TIMEOUT_ASSIGNRES)

    assert device.get_attribute("State") == state
    assert device.get_attribute("obsState") == obs_state


def wait_for_obs_state(device, obs_state, timeout=TIMEOUT):
    """
    Wait for obsState to have the expected value.

    :param device: device proxy
    :param obs_state: the expected value
    :param timeout: timeout in seconds
    """

    def predicate():
        return device.get_attribute("obsState") == obs_state

    description = f"obsState {obs_state}"
    wait_for_predicate(predicate, description, timeout=timeout)
