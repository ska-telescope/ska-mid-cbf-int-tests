# Documentation for notebook_params.json parameters

- deployer: parameters related to CBF EC Deployer (will be removed in AA2+)
    - talons List[int]: target talons for CBF MCS Controller to use
- controller: parameters related to CBF MCS Controller
    - init_sys_param_id [str]: ID of init_sys_param json to use for InitSysParam command from ska_mid_cbf_int_tests.cbf_data.init_sys_param
- recording: parameters related to execution recording/logging configuration
    - asserting [bool]: whether to raise AssertionErrors on command failures or not
- scan: parameters related to the CBF MCS Subarray Scan run
    - subarray_no [int]: subarray number to run scan on
    - receptors List[str]: receptor resources to collect data from in form necessary for MCS Subarray AddReceptors command (e.g. ["SKA001", "SKA063"])
    - scan_config_id [str]: ID of scan configuration json to use for ConfigureScan command from ska_mid_cbf_int_tests.cbf_data.configure_scan
    - scan_id [str]: ID of scan json to use for Scan command from ska_mid_cbf_int_tests.cbf_data.scan
- tango_host_connection: parameters related to setting up the TANGO_HOST connection
    - namespace_tango_db_address [str]: [likely unnecessary to change] TANGO database address in Kubernetes namespace in form \<hostname\>:\<port\> (default: databaseds-tango-base:10000)
    - kube_namespace [str]: name of Kubernetes namespace created in a int-tests Gitlab pipeline (see main repository README)
    - kube_cluster_domain [str]: [likely unnecessary to change] domain name of Kubernetes cluster that Kubernetes namespace is run within (default: cluster.local)