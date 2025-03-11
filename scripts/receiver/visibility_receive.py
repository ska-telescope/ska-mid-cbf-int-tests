"""Visibility receive test."""

# pylint: disable=import-error
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name

import contextlib
import json
import logging
import os
import random
import tempfile
import time

import pytest
import yaml
from common import (
    Comparison,
    K8sElementManager,
    check_data_copied,
    compare_data,
    compare_scan,
    copy_data,
    pvc_exists,
    tango_client,
    wait_for_pod,
)
from conftest import (
    Context,
)
from test_subarray import (
    TIMEOUT_ASSIGNRES,
    TRANSLATIONS,
    call_command,
    create_id,
    read_command_argument,
    read_json_data,
    set_state_and_obs_state,
    wait_for_obs_state,
)

LOG = logging.getLogger(__name__)

RECEIVE_POD = "resources/sdp-test-visibility-receive-pod.yaml"


def read_assign_resources_config(context):
    """
    Read the AssignResources config for visibility receive.

    Substitutes randomly-generated IDs so the test can be run more than once in
    the same instance of SDP. The config is used in more than one step in the
    test, so it must be a fixture.

    """
    config = read_json_data("visibility_receive.json")

    config["execution_block"]["eb_id"] = create_id("eb")
    for pblock in config["processing_blocks"]:
        pblock["pb_id"] = create_id("pb")
        pb_params = pblock["parameters"]
        pb_params["pvc"]["name"] = context.pvc_name
        for init_container in pb_params["plasma_parameters"]["initContainers"]:
            init_container["volumeMounts"][0]["name"] = context.pvc_name
        pb_params["plasma_parameters"]["extraContainers"][0]["volumeMounts"][
            1
        ]["name"] = context.pvc_name

    return config


def dataproduct_directory(assign_resources_config):
    """
    The directory where output files will be written.

    :param assign_reso
    urces_config: AssignResources configuration
    """
    eb_id = assign_resources_config["execution_block"]["eb_id"]
    pb_id = assign_resources_config["processing_blocks"][0]["pb_id"]
    return f"/product/{eb_id}/ska-sdp/{pb_id}"


def run_vis_receive_script(
    subarray_device, k8s_element_manager, assign_resources_config
):
    """
    Start the visibility receive script and end it after the test.

    This uses the k8s_element_manager fixture to ensure the script is ended
    before the PVCs are removed.

    :param subarray_device: SDP subarray device client
    :param k8s_element_manager: Kubernetes element manager
    :param assign_resources_config: AssignResources configuration

    """

    # Start the script

    LOG.info("Calling AssignResources")
    subarray_device.execute_command(
        "AssignResources", argument=json.dumps(assign_resources_config)
    )

    yield

    LOG.info("Calling End")
    subarray_device.execute_command("End")
    wait_for_obs_state(subarray_device, "IDLE", timeout=30)

    # End the script
    LOG.info("Calling ReleaseAllResources")
    subarray_device.execute_command("ReleaseAllResources")


def subarray_scan(subarray_device):
    """
    Execute a scan.

    :param subarray_device: SDP subarray device client

    """
    timeout = 30
    configure_command = read_command_argument("Configure")
    scan_command = read_command_argument("Scan")

    @contextlib.contextmanager
    def subarray_do_scan(scan_id, scan_type_id, prev_scan_type=None):
        # If previous scan_type is same as the current scan type
        # then don't need to run Configure command
        if scan_type_id != prev_scan_type:
            # Configure
            LOG.info("Calling Configure(scan_type=%s)", scan_type_id)
            configure_command["scan_type"] = scan_type_id
            subarray_device.execute_command(
                "Configure",
                argument=json.dumps(configure_command),
            )
            wait_for_obs_state(subarray_device, "READY", timeout=timeout)

        # Scan
        LOG.info("Calling Scan(scan_id=%d)", scan_id)
        scan_command["scan_id"] = scan_id
        subarray_device.execute_command("Scan", json.dumps(scan_command))
        wait_for_obs_state(subarray_device, "SCANNING", timeout=timeout)

        try:
            yield
        finally:
            # Revert back to IDLE
            LOG.info("Calling EndScan")
            subarray_device.execute_command("EndScan")
            wait_for_obs_state(subarray_device, "READY", timeout=timeout)

    return subarray_do_scan


# -----------
# Given steps
# -----------

def connect_to_subarray(context):
    """
    Connect to the subarray device.

    :param context: context for the tests
    :returns: SDP subarray device client

    """
    return tango_client(
        context, context.subarray_device, translations=TRANSLATIONS
    )

def set_obs_state(subarray_device, obs_state):
    """
    Set the obsState to the desired value.

    This function sets the device state to ON.

    :param subarray_device: SDP subarray device client
    :param obs_state: desired obsState

    """
    set_state_and_obs_state(subarray_device, "ON", obs_state)


def local_volume(context, k8s_element_manager):
    """
    Check if the local volumes are created and data is copied.

    :param context: context for the tests
    :param k8s_element_manager: Kubernetes element manager
    """

    LOG.info("Check for existing PVC")
    pvc_exists(context.pvc_name, context.namespace_sdp)


    LOG.info("Create Pod for receiver and sender")
    k8s_element_manager.create_pod(
        RECEIVE_POD, context.namespace_sdp, context.pvc_name
    )


    # Wait for pods
    assert wait_for_pod("receive-data", context.namespace_sdp, "Running", 300)


    # Copy the measurement set to receive and sender containers
    ms_file = "resources/data/AA05LOW.ms/"
    ms_file_mount_location = "/mnt/data/AA05LOW.ms/"

    # Copy data to receive and sender pod
    receive_pod = "receive-data"
    receive_container = "receive-data-prep"

    copy_data(
        ms_file,
        ms_file_mount_location,
        receive_pod,
        receive_container,
        context.namespace_sdp,
    )

    receiver_result = check_data_copied(
        receive_pod,
        receive_container,
        context.namespace_sdp,
        ms_file_mount_location,
    )


    assert receiver_result.returncode == 0
    LOG.info("PVCs and pods created, and data copied successfully")


def deploy_script(
    context, subarray_device, assign_resources_config, k8s_element_manager
):
    """
    Deploy visibility receive script.

    This uses the vis_receive_script fixture to automatically end the
    script when the test is finished.

    :param vis_receive_script: visibility receive script fixture
    :param context: context for the tests
    :param subarray_device: SDP subarray device client
    :param assign_resources_config: AssignResources configuration

    """
    next(
        run_vis_receive_script(subarray_device, k8s_element_manager, assign_resources_config)
    )
    # Check the obsState becomes the expected value
    wait_for_obs_state(subarray_device, "IDLE", timeout=TIMEOUT_ASSIGNRES)

    pb_id = assign_resources_config["processing_blocks"][0]["pb_id"]
    receiver_pod_name = f"proc-{pb_id}-receive-0"

    print("WAITING FOR POD")
    

    # Check if the receiver is running
    #assert wait_for_pod(
    #    receiver_pod_name,
    #    context.namespace_sdp,
    #    "Running",
    #    600,
    #    pod_condition="Ready",
    #)

def subarray_ready(subarray_device):
    """
    Execute a scan.

    :param subarray_device: SDP subarray device client

    """
    timeout = 30
    configure_command = read_command_argument("Configure")
    scan_command = read_command_argument("Scan")

    @contextlib.contextmanager
    def subarray_ready():
        # We don't Configure() here as each scan will do their own
        # configuration depending on the scan type.
        wait_for_obs_state(subarray_device, "IDLE", timeout=timeout)

        yield subarray_do_scan

        # Can't be called in fixture as we need this to terminate the receive
        # containers so all files are flushed and closed by the time we verify
        # their contents.
        LOG.info("Calling End")
        subarray_device.execute_command("End")
        wait_for_obs_state(subarray_device, "IDLE", timeout=30)

    @contextlib.contextmanager
    def subarray_do_scan(scan_id, scan_type_id, prev_scan_type=None):
        # If previous scan_type is same as the current scan type
        # then don't need to run Configure command
        if scan_type_id != prev_scan_type:
            # Configure
            LOG.info("Calling Configure(scan_type=%s)", scan_type_id)
            configure_command["scan_type"] = scan_type_id
            subarray_device.execute_command(
                "Configure",
                argument=json.dumps(configure_command),
            )
            wait_for_obs_state(subarray_device, "READY", timeout=timeout)



        # Scan
        LOG.info("Calling Scan(scan_id=%d)", scan_id)
        scan_command["scan_id"] = scan_id
        subarray_device.execute_command("Scan", json.dumps(scan_command))
        wait_for_obs_state(subarray_device, "SCANNING", timeout=timeout)


        try:
            yield
        finally:
            # Revert back to IDLE
            LOG.info("Calling EndScan")
            subarray_device.execute_command("EndScan")
            wait_for_obs_state(subarray_device, "READY", timeout=timeout)

    return subarray_ready


def run_scans(
    context, telescope, subarray_device, k8s_element_manager
):
    """
    Run a sequence of scans.

    :param context: context for the tests
    :param telescope: the SKA telescope for which to emulate data sending
    :param subarray_device: SDP subarray device client
    :param subarray_ready: subarray fixture
    :param k8s_element_manager: Kubernetes element manager

    """

    ready_subarray = subarray_ready(subarray_device)

    # Setting number of scans
    context.nscan = 2

    receive_addresses = json.loads(
        subarray_device.get_attribute("receiveAddresses")
    )

    with ready_subarray() as do_scan:
        for scan_id, scan_type in ((1, "science"), (2, "calibration")):
            host = receive_addresses[scan_type]["vis0"]["host"][0][1]
            with do_scan(scan_id, scan_type):
                import time
                time.sleep(120)




if __name__ == '__main__':
    print('test')

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
    #tango_client = "gql"
    # Kubernetes namespace
    namespace = "ci-ska-skampi-cip-1389-prototype-sdp-receiver-mid"
    namespace_sdp = "ci-ska-skampi-cip-1389-prototype-sdp-receiver-mid-sdp"
    # Telescope (Skampi pipeline sets this to "SKA-Low" or "SKA-Mid")
    telescope = "mid"
    pvc_name = "ska-sdp-pvc"

    prefix = "mid"

    # Tango device names
    subarray_device = f"{prefix}-sdp/subarray/01"
    # Name of subarray device server stateful set
    subarray_stateful_set = subarray_stateful_set

    ingress = "http://rmdskadevdu011/"

    tangogql_url = f"{ingress}/{namespace}/taranta"

    qa_metric_host = f"{ingress}/{namespace}/qa/api"

    test_context = Context()

    # Set default number of scans
    test_context.nscan = 0

    # Namespace
    test_context.namespace = namespace
    test_context.namespace_sdp = namespace_sdp
    # Tango client
    test_context.tango_client = tango_client
    test_context.subarray_device = f"{prefix}-sdp/subarray/01"
    test_context.tango_client = "gql"
    test_context.tangogql_url = f"{ingress}/{namespace}/tangogql"
    test_context.pvc_name = "ska-sdp-pvc"

    manager = K8sElementManager()

    subarray_device = tango_client(test_context, test_context.subarray_device, translations=TRANSLATIONS)
    connect_to_subarray(test_context)
    #set_obs_state(subarray_device, "EMPTY")
    local_volume(test_context, manager)
    assign_resources_config = read_assign_resources_config(test_context)
    #set_obs_state(subarray_device, "IDLE")
    deploy_script(test_context, subarray_device, assign_resources_config, manager)
    run_scans(test_context, "mid", subarray_device, manager)


