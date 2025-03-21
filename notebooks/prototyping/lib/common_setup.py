"""TODO"""

from pathlib import Path

from common_notebook_package import CommonNotebookPkg

NOTEBOOK_PARAM_JSON = (
    Path.resolve(__file__).parents[1] / "notebook_params.json"
)


def common_notebook_setup() -> CommonNotebookPkg:
    """TODO"""
    return CommonNotebookPkg(NOTEBOOK_PARAM_JSON)
