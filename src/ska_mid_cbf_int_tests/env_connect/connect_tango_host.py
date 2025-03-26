"""Manages connection to TANGO_HOST."""

import os


def connect_tango_host(
    kube_namespace: str,
    tango_host: str,
    cluster_domain: str,
):
    """TODO"""
    tango_hostname, tango_port = tango_host.split(":")
    os.environ[
        "TANGO_HOST"
    ] = f"{tango_hostname}.{kube_namespace}.svc.{cluster_domain}:{tango_port}"
