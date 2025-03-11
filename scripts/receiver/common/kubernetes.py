"""Kubernetes utilities for tests."""
import enum
import logging
import subprocess
import time

import yaml
from kubernetes import client, config, watch
from kubernetes.stream import stream

LOG = logging.getLogger(__name__)

TIMEOUT = 15

config.load_config()


def k8s_pod_exec(
    exec_command,
    pod_name,
    container_name,
    namespace,
    stdin=True,
    stdout=True,
    stderr=True,
):
    """Execute a command in a Kubernetes Pod

    param exec_command: command to be executed (eg ["bash", "-c", tar_command])
    param pod_name: Pod name
    param container_name: Container name
    param namespace: Namespace
    param stdin: Enable stdin on channel
    param stdout: Enable stdout on channel
    param stderr: Enable stderr on channel

    returns api_response: Channel connection object
    """
    # pylint: disable=too-many-arguments

    # Get API handle
    core_api = client.CoreV1Api()
    LOG.debug(
        "Executing command in container %s/%s/%s: %s",
        namespace,
        pod_name,
        container_name,
        "".join(exec_command),
    )

    api_response = stream(
        core_api.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=exec_command,
        container=container_name,
        stderr=stderr,
        stdin=stdin,
        stdout=stdout,
        tty=False,
        _preload_content=False,
    )

    return api_response


def consume_response(api_response):
    """Consumes and logs the stdout/stderr from a stream response

    :param api_response: stream with the results of a pod command execution
    """
    while api_response.is_open():
        api_response.update(timeout=1)
        if api_response.peek_stdout():
            LOG.info("STDOUT: %s", api_response.read_stdout().strip())
        if api_response.peek_stderr():
            LOG.info("STDERR: %s", api_response.read_stderr().strip())
    api_response.close()


def pod_exists(namespace: str, pod_file: str):
    """Check if the pod from a file definition exists.

    :param namespace: namespace
    :param pod_file: yaml file for pod

    """
    core_api = client.CoreV1Api()

    pod_spec = convert_yaml_file(pod_file)

    k8s_pods = core_api.list_namespaced_pod(namespace)
    for item in k8s_pods.items:
        if item.metadata.name == pod_spec["metadata"]["name"]:
            return True
    return False


def pod_list(namespace: str):
    """Get a list of pods for a namespace.

    :param namespace: namespace

    """
    core_api = client.CoreV1Api()

    k8s_pods = core_api.list_namespaced_pod(namespace)

    return [item.metadata.name for item in k8s_pods.items]


def create_pod(pod_file: str, namespace: str, pvc_name: str):
    """Create namespaced pod.

    :param pod_file: yaml file for pod
    :param namespace: namespace
    :param pvc_name: name of the sdp data pvc

    """
    # Get API handle
    core_api = client.CoreV1Api()

    pod_spec = convert_yaml_file(pod_file)

    # Update the name of the data pvc
    pod_spec["spec"]["volumes"][0]["persistentVolumeClaim"][
        "claimName"
    ] = pvc_name

    # Check Pod does not already exist
    k8s_pods = core_api.list_namespaced_pod(namespace)
    for item in k8s_pods.items:
        assert (
            item.metadata.name != pod_spec["metadata"]["name"]
        ), f"Pod {item.metadata.name} already exists"

    LOG.info("Creating Pod from %s in namespace %s", pod_file, namespace)

    core_api.create_namespaced_pod(namespace, pod_spec)


def pvc_exists(pvc_name: str, namespace: str):
    """Check if the pvc from the env variable exists.

    :param pvc_name: name of the sdp data pvc

    """
    core_api = client.CoreV1Api()

    k8s_pvc = core_api.list_namespaced_persistent_volume_claim(namespace)
    for item in k8s_pvc.items:
        if item.metadata.name == pvc_name:
            return True
    return False


def create_pvc(pvc_file: str, namespace: str):
    """Create namespaced persistent volume claim.

    :param pvc_file: yaml file for persistent volume claim
    :param namespace: namespace

    """
    # Get API handles
    core_api = client.CoreV1Api()
    storage_api = client.StorageV1Api()

    pvc_spec = convert_yaml_file(pvc_file)

    # Check for existing PVC
    k8s_pvc = core_api.list_namespaced_persistent_volume_claim(namespace)
    for item in k8s_pvc.items:
        if item.metadata.name == pvc_spec["metadata"]["name"]:
            LOG.info("PVC %s already exists", item.metadata.name)
            assert (
                item.status.phase == "Bound"
            ), f"PVC not in expected state - {item.status.phase}"
            return

    LOG.info("Creating PVC from %s in namespace %s", pvc_file, namespace)

    storage_class = pvc_spec["spec"]["storageClassName"]
    k8s_sc = storage_api.list_storage_class()
    for item in k8s_sc.items:
        if item.metadata.name == storage_class:
            break

    assert (
        item.metadata.name == storage_class
    ), f"Storage class {storage_class} not defined"

    # Create new PVC
    core_api.create_namespaced_persistent_volume_claim(namespace, pvc_spec)


def copy_data(
    ms_file: str,
    mount_location: str,
    pod_name: str,
    container_name: str,
    namespace: str,
):
    """Copy measurement set data to receive and sender containers.

    :param ms_file: measurement set file
    :param mount_location: mount location for data in the containers
    :param pod_name: name of the pod
    :param container_name: name of the container
    :param namespace: namespace
    """

    LOG.info("Copying %s to Pod %s:%s", ms_file, pod_name, mount_location)
    cmd = (
        f"kubectl cp {ms_file} {namespace}/{pod_name}:{mount_location} "
        f"-c {container_name}"
    )
    subprocess.run(cmd, shell=True, check=True)


def delete_pod(pod_file: str, namespace: str, timeout=40):
    """Delete namespaced pod.

    :param pod_file: yaml file for pod
    :param namespace: namespace
    """
    # Get API handle
    core_api = client.CoreV1Api()

    data = convert_yaml_file(pod_file)
    core_api.delete_namespaced_pod(
        data["metadata"]["name"], namespace, async_req=False
    )
    time_between_checks = 0.2
    while timeout > 0 and pod_exists(namespace, pod_file):
        time.sleep(time_between_checks)
        timeout -= time_between_checks
    if timeout <= 0 and pod_exists(namespace, pod_file):
        raise AssertionError(
            f"Pod {pod_file} didn't disappear in {timeout} seconds"
        )


def delete_pvc(pod_file: str, namespace: str):
    """Delete namespaced persistent volume claim.

    :param pod_file: yaml file for pod
    :param namespace: namespace
    """

    # Get API handle
    core_api = client.CoreV1Api()

    data = convert_yaml_file(pod_file)
    core_api.delete_namespaced_persistent_volume_claim(
        data["metadata"]["name"], namespace, async_req=False
    )


def scale_stateful_set(
    namespace: str, name: str, replicas: int, timeout: int = TIMEOUT
):
    """
    Scale a stateful set.

    :param namespace: namespace
    :param name: name of stateful set
    :param replicas: number of replicas
    :param timeout: time to wait for the change

    """
    # Get apps API handle
    apps_api = client.AppsV1Api()

    # Patch stateful set scale to set number of replicas
    body = {"spec": {"replicas": replicas}}
    apps_api.patch_namespaced_stateful_set_scale(name, namespace, body)

    # Wait until the number of ready replicas is as desired
    # If the number is zero, it is reported in the status as "None"
    target = replicas if replicas else None
    watch_sts = watch.Watch()
    for event in watch_sts.stream(
        apps_api.list_namespaced_stateful_set,
        namespace,
        timeout_seconds=timeout,
    ):
        obj = event["object"]
        if obj.metadata.name == name and obj.status.ready_replicas == target:
            watch_sts.stop()


class Comparison(enum.Enum):
    """Comparisons for waiting for pods."""

    # pylint: disable=unnecessary-lambda-assignment

    EQUALS = lambda x, y: x == y  # noqa: E731
    CONTAINS = lambda x, y: x in y  # noqa: E731


def wait_for_pod(
    pod_name: str,
    namespace: str,
    phase: str,
    timeout: int = TIMEOUT,
    name_comparison: Comparison = Comparison.EQUALS,
    pod_condition: str = "",
):
    """Wait for the pod to be Running.

    :param pod_name: name of the pod
    :param namespace: namespace
    :param phase: phase of the pod
    :param timeout: time to wait for the change
    :param name_comparison: the type of comparison used to match a pod name
    :param pod_condition: if given, the condition through which the pod must
    have passed

    :returns: whether the pod was in the indicated status within the timeout
    """
    # pylint: disable=too-many-arguments

    # Get API handle
    core_api = client.CoreV1Api()

    if pod_condition:

        def check_condition(pod):
            return any(
                c.status == "True"
                for c in pod.status.conditions
                if c.type == pod_condition
            )

    else:

        def check_condition(_):
            return True

    watch_pod = watch.Watch()
    for event in watch_pod.stream(
        func=core_api.list_namespaced_pod,
        namespace=namespace,
        timeout_seconds=timeout,
    ):
        pod = event["object"]
        if (
            name_comparison(pod_name, pod.metadata.name)
            and pod.status.phase == phase
            and check_condition(pod)
        ):
            watch_pod.stop()
            return True
    return False


def check_data_copied(
    pod_name: str, container_name: str, namespace: str, mount_location: str
):
    """Check if the data copied into the pod correctly.

    :param pod_name: name of the pod
    :param container_name: name of the container
    :param namespace: namespace
    :param mount_location: mount location for data in the containers

    :returns: exit code of the command
    """

    exec_command = ["ls", mount_location]
    resp = k8s_pod_exec(
        exec_command,
        pod_name,
        container_name,
        namespace,
        stdin=False,
        stdout=False,
    )
    consume_response(resp)
    return resp


def compare_data(
    pod_name: str, container_name: str, namespace: str, measurement_set: str
):
    """Compare the data sent with the data received.

    :param pod_name: name of the pod
    :param container_name: name of the container
    :param namespace: namespace
    :param measurement_set: name of the Measurement Set to compare

    :returns: exit code of the command
    """
    # To test if the sent and received data match using ms-asserter

    exec_command = [
        "ms-asserter",
        "/mnt/data/AA05LOW.ms",
        f"/mnt/data/{measurement_set}",
        "--minimal",
        "true",
    ]
    resp = k8s_pod_exec(
        exec_command, pod_name, container_name, namespace, stdin=False
    )
    consume_response(resp)
    return resp


def compare_scan(
    pod_name: str,
    container_name: str,
    namespace: str,
    measurement_set: str,
    expected_scan_id: int,
):
    """Compare the data sent with the data received.

    :param pod_name: name of the pod
    :param container_name: name of the container
    :param namespace: namespace
    :param measurement_set: name of the Measurement Set to read
    :param scan_id: the ID of the scan expected to be recorded in the
        Measurement Set
    """

    with open(
        "tests/resources/scripts/compare_scan.py", encoding="utf-8"
    ) as script_file:
        python_script = script_file.read()
    cmd = [
        "python",
        "-c",
        python_script,
        f"/mnt/data/{measurement_set}",
        str(expected_scan_id),
    ]

    resp = k8s_pod_exec(cmd, pod_name, container_name, namespace, stdin=False)
    consume_response(resp)
    assert resp.returncode == 0


def get_pvc(namespaces):
    """Get the persistent volume claims.

    :param namespaces: list of namespaces

    :returns: list of persistent volume claims
    """
    persistent_volume_claims = []

    # Get API handle
    core_api = client.CoreV1Api()

    # Get a list of the persistent volume claims
    for namespace in namespaces:
        pvcs = core_api.list_namespaced_persistent_volume_claim(
            namespace=namespace, watch=False
        )
        for pvc in pvcs.items:
            persistent_volume_claims.append(pvc.metadata.name)

    return persistent_volume_claims


def convert_yaml_file(file: str):
    """Convert yaml file to python object.

    :param file: yaml file

    :returns: python object which contains parameters
    """

    with open(file, "r", encoding="utf-8") as istream:
        converted = yaml.safe_load(istream)

    return converted


def helm_install(release, chart, namespace, values_file):
    """Install a Helm chart

    :param release: The name of the release
    :param chart: The name of the chart
    :param namespace: The namespace where the chart will be installed
    :param values_file: A file with values to be handed over to the chart
    """

    cmd = [
        "helm",
        "install",
        release,
        chart,
        "-n",
        namespace,
        "-f",
        values_file,
        "--wait",
    ]
    subprocess.run(cmd, check=True)


def delete_directory(
    dataproduct_directory, pod_name, container_name, namespace
):
    """Delete a directory

    :param dataproduct_directory: The directory where outputs are written
    :param pod_name: name of the pod
    :param container_name: name of the container
    :param namespace: The namespace where the chart will be installed

    """
    del_command = ["rm", "-rf", f"/mnt/data/{dataproduct_directory}"]
    resp = k8s_pod_exec(
        del_command, pod_name, container_name, namespace, stdin=False
    )
    consume_response(resp)
    assert resp.returncode == 0


def helm_uninstall(release, namespace):
    """Uninstall a Helm chart

    :param release: The name of the release
    :param namespace: The namespace where the chart lives
    """
    cmd = [
        "helm",
        "uninstall",
        release,
        "-n",
        namespace,
        "--wait",
        "--no-hooks",
    ]
    subprocess.run(cmd, check=True)


class K8sElementManager:
    """
    An object that keeps track of the k8s elements it creates, the order in
    which they are created, how to delete them, so that users can perform this
    reverse deletion on request.
    """

    def __init__(self):
        self.to_remove = []

    def cleanup(self):
        """
        Delete all known created objects in the reverse order in which they
        were created.
        """
        LOG.info("Run cleanup")
        for cleanup_function, data in self.to_remove[::-1]:
            cleanup_function(*data)

    def create_pvc(self, *pvc):
        """Create the requested PVC."""
        create_pvc(*pvc)

    def create_pod(self, pod_file, namespace, pvc_name):
        """Create the requested POD and keep track of it for later deletion."""
        create_pod(pod_file, namespace, pvc_name)
        self.to_remove.append((delete_pod, (pod_file, namespace)))

    def helm_install(self, release, chart, namespace, values_file):
        """
        Install the requested Helm chart and keep track of it for later
        deletion.
        """
        helm_install(release, chart, namespace, values_file)
        self.to_remove.append((helm_uninstall, (release, namespace)))

    def output_directory(
        self, dataproduct_directory, pod_name, container_name, namespace
    ):
        """Remove the output directory once the test is finished."""
        self.to_remove.append(
            (
                delete_directory,
                (dataproduct_directory, pod_name, container_name, namespace),
            )
        )
