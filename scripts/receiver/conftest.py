"""Test configuration."""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes

import os
from types import SimpleNamespace

import pytest
from common import K8sElementManager


class Context(SimpleNamespace):
    """Generic holder for context information."""


@pytest.fixture(scope="session")
def context():
    """Get context for tests from environment."""

    # Constants
    tangogql_service = "ska-sdp-test-tangogql"
    tangogql_port = "5004"
    subarray_stateful_set = "ska-sdp-lmc-subarray-01"

    # Read environment variables....

    # Ingress to connect to the cluster - if not set, the test is assumed to be
    # running inside the cluster
    ingress = os.environ.get("TEST_INGRESS")
    # Tango device client (specific to SDP integration):
    # "dp" = use Pytango device proxy
    # "gql" = use TangoGQL
    tango_client = os.environ.get("TEST_TANGO_CLIENT", "dp")
    # Kubernetes namespace
    namespace = os.environ.get("KUBE_NAMESPACE")
    namespace_sdp = os.environ.get("KUBE_NAMESPACE_SDP")
    # Telescope (Skampi pipeline sets this to "SKA-Low" or "SKA-Mid")
    telescope = os.environ.get("SKA_TELESCOPE", None)
    pvc_name = os.environ.get("SDP_DATA_PVC_NAME", None)

    # Set prefix for Tango device names
    if telescope:
        # Testing Skampi deployment, so set to "low" or "mid" as appropriate
        prefix = telescope[4:7].lower()
    else:
        # Use default prefix
        prefix = "test"

    # Create the context to be passed to the tests
    test_context = Context()

    # Set default number of scans
    test_context.nscan = 0

    # Namespace
    test_context.namespace = namespace
    test_context.namespace_sdp = namespace_sdp
    # Tango client
    test_context.tango_client = tango_client
    # Tango device names
    test_context.exchange_device = f"{prefix}-sdp/exchange/0"
    test_context.qametric_device = f"{prefix}-sdp/qametrics/0"
    test_context.controller_device = f"{prefix}-sdp/control/0"
    test_context.subarray_device = f"{prefix}-sdp/subarray/01"
    # Name of subarray device server stateful set
    test_context.subarray_stateful_set = subarray_stateful_set
    # Name of PVC
    test_context.pvc_name = pvc_name

    if tango_client == "gql":
        # Set TangoGQL server URL
        if ingress:
            # Test is running outside cluster, so use ingress
            test_context.tangogql_url = f"{ingress}/{namespace}/tangogql"
        else:
            # Test is running inside cluster, so connect to service directly
            test_context.tangogql_url = (
                f"http://{tangogql_service}.{namespace}:{tangogql_port}"
            )

    if ingress:
        test_context.qa_metric_host = f"{ingress}/{namespace}/qa/api"
    else:
        test_context.qa_metric_host = f"http://ska-sdp-qa-api.{namespace}:8002"

    return test_context


@pytest.fixture(scope="module")
def k8s_element_manager():
    """Allow easy creation, and later automatic destruction, of k8s elements"""
    manager = K8sElementManager()
    yield manager
    manager.cleanup()
