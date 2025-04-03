#!/bin/bash

# Collect all logs from pods Kuberenetes namespace of $1 generated in the last
# CAPTURE_LOGS_SINCE_N_HOURS hours and save them into LOGS_DIR.
# param $1: name of Kubernetes namespace

KUBE_NAMESPACE=$1

SCRIPT_DIR=$(dirname "$0")
LOGS_DIR="$SCRIPT_DIR/../../logs"

mkdir -p $LOGS_DIR

CAPTURE_LOGS_SINCE_N_HOURS=5
POD_LIST=$(kubectl get pods -n $KUBE_NAMESPACE --no-headers -o custom-columns=":metadata.name")
for POD in ${POD_LIST[@]}; do
    KUBE_POD_LOG_CAPTURE_CMD="kubectl logs ${POD} -n ${KUBE_NAMESPACE} --since=${CAPTURE_LOGS_SINCE_N_HOURS}h &> ${LOGS_DIR}/${POD}.log"
    echo $KUBE_POD_LOG_CAPTURE_CMD
    eval $KUBE_POD_LOG_CAPTURE_CMD
done