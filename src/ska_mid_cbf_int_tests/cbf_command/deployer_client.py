"""TODO"""
from __future__ import annotations

from typing import List

from .device_client import DeviceClient


class DeployerClient(DeviceClient):
    """TODO"""

    def __init__(
        self: DeployerClient,
        device_fqdn: str,
        device_timeout_sec: float,
    ):
        super().__init__(device_fqdn, device_timeout_sec, None)

    def wr_target_talons(self: DeployerClient, talon_ids: List[int]):
        """TODO"""
        self.proxy.write_attribute("targetTalons", talon_ids)

    def generate_config_jsons(self: DeployerClient):
        """TODO"""
        self.proxy.command_inout("generate_config_jsons")
