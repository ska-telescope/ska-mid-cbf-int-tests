"""Mid.CBF TANGO Device Related Constants."""

LRC_ATTR_NAME = "longRunningCommandResult"

DEPLOYER_FQDN = "mid_csp_cbf/ec/deployer"
CONTROLLER_FQDN = "mid_csp_cbf/sub_elt/controller"


def gen_subarray_fqdn(subarray_no: int) -> str:
    """
    Generates a subarray FQDN for the given id number of subarray_no.

    :param subarray_no: id number of the subarray to generate the FQDN for
    :returns str: FQDN for subarray associated with subarray_no
    """
    return f"mid_csp_cbf/sub_elt/subarray_{subarray_no:02}"
