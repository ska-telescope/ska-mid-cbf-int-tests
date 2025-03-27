# Documentation for notebook_params.json parameters

- deployer: parameters related to CBF EC Deployer (will be removed in AA2+)
    - talons: target talons for CBF MCS Controller to use
- controller: parameters related to CBF MCS Controller
    - init_sys_param_id: ID of init_sys_param json to use for InitSysParam command from ska_mid_cbf_int_tests.cbf_data.init_sys_param
- recording: parameters related to execution recording/logging configuration
    - asserting: whether to raise AssertionErrors on command failures or not (true/false)
- scan: parameters related to the CBF MCS Subarray Scan run
    - subarray_no: subarray number to run scan on
    - receptors: receptor resources to collect data from
    - scan_config_id: ID of scan configuration json to use for ConfigureScan command from ska_mid_cbf_int_tests.cbf_data.configure_scan
    - scan_id: ID of scan json to use for Scan command from ska_mid_cbf_int_tests.cbf_data.scan
- tango_host_connection: parameters related to setting up the TANGO_HOST connection
    - namespace_tango_db_address: [likely unnecessary to change] TANGO database address in Kubernetes namespace in form \<hostname\>:\<port\> (default: databaseds-tango-base:10000)
    - kube_namespace: name of Kubernetes namespace created in a int-tests Gitlab pipeline (see main repository README)
    - kube_cluster_domain: [likely unnecessary to change] domain name of Kubernetes cluster that Kubernetes namespace is run within (default: cluster.local)