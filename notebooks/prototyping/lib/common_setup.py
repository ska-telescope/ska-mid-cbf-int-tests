"""TODO"""

from pathlib import Path

from ska_mid_cbf_int_tests.env_connect.connect_tango_host import (
    connect_tango_host,
)

from .common_notebook_package import CommonNotebookPkg

NOTEBOOK_PARAM_JSON = (
    Path.resolve(Path(__file__)).parents[1] / "notebook_params.json"
)


def common_notebook_setup() -> CommonNotebookPkg:
    """TODO"""

    common_notebook_pkg = CommonNotebookPkg(NOTEBOOK_PARAM_JSON)

    connect_tango_host(
        common_notebook_pkg.namespace_tango_db_address,
        common_notebook_pkg.kube_namespace,
        common_notebook_pkg.kube_cluster_domain,
    )

    return common_notebook_pkg
