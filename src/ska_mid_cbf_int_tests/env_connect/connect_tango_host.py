"""Manages connection to TANGO_HOST."""

import os


def connect_tango_host(
    namespace_tango_db_address: str,
    kube_namespace: str,
    kube_cluster_domain: str,
):
    """
    Connect OS environment to TANGO_HOST for all tango access.

    :param namespace_tango_db_address: tango DB address in namespace
    :param kube_namespace: kubernetes namespace in cluster
    :param kube_cluster_domain: kubernetes cluster domain
    """
    db_hostname, db_port = namespace_tango_db_address.split(":")

    # See:
    # https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
    # and
    full_tango_database_address = (
        f"{db_hostname}.{kube_namespace}.svc.{kube_cluster_domain}:{db_port}"
    )

    # See:
    # https://tango-controls.readthedocs.io/en/latest/development/advanced/reference.html#environment-variables
    os.environ["TANGO_HOST"] = full_tango_database_address
