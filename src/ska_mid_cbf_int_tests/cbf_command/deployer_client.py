"""Module for DeployerClient code."""
from __future__ import annotations

from typing import List

from ska_mid_cbf_int_tests.constants.timeout_constants import (
    DEFAULT_DEVICE_TIMEOUT,
)

from .device_client import DeviceClient


class DeployerClient(DeviceClient):
    """
    API Client for controlling the EC Deployer.

    Note: Likely will be deleted for AA2+ as TDC is left behind.
    """

    def __init__(self: DeployerClient, device_fqdn: str):
        """
        Create instance of DeployerClient

        :param device_fqdn: FQDN of deployer tango device.
        """
        super().__init__(device_fqdn, DEFAULT_DEVICE_TIMEOUT, None)

    def _prep_alobserver_tracer(self: DeployerClient):
        """No subscriptions necessary for DeployerClient."""

    def wr_target_talons(self: DeployerClient, talon_nos: List[int]):
        """
        Write target talons to be used by CBF controller.

        :param talon_nos: list of talon numbers for cbfcontroller to use
        """
        self.proxy.write_attribute("targetTalons", talon_nos)

    def generate_config_jsons(self: DeployerClient):
        """
        Copies config_commands.json into the shared kubernetes
        storage provisions with CBF Controller in the artifacts directory for
        controller On() and Off() commands. Also generates JSONs for TDC
        deployment but is irrelevant for non-TDC usage.
        """
        self.proxy.command_inout("generate_config_jsons")
