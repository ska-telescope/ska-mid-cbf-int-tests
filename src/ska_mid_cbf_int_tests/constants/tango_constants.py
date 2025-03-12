"""TODO"""
LRC_ATTR_NAME = "longRunningCommandResult"

DEPLOYER_FQDN = "mid_csp_cbf/ec/deployer"
CONTROLLER_FQDN = "mid_csp_cbf/sub_elt/controller"


def gen_subarray_fqdn(subarray_no: int):
    """TODO"""
    return f"mid_csp_cbf/sub_elt/subarray_{subarray_no:02}"
