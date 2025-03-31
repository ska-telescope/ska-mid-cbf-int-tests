#!/bin/bash

# Collect all image versions from Kuberenetes namespace of $1 and saves
# the summary of them them into LOGS_DIR at $NAMESPACE_POD_IMAGES_FILE.
# param $1: name of Kubernetes namespace

KUBE_NAMESPACE=$1

SCRIPT_DIR=$(dirname "$0")
LOGS_DIR="$SCRIPT_DIR/../../logs"

mkdir -p $LOGS_DIR

NAMESPACE_POD_IMAGES_FILE="$LOGS_DIR/pod_image_summary.txt"

POD_INFO_TABLE_OUT="Pod Image"
POD_INFO_TABLE_OUT+=$'\n'
POD_LIST=$(kubectl get pods -n $KUBE_NAMESPACE --no-headers -o custom-columns=":metadata.name")
for POD in ${POD_LIST[@]}; do
    POD_IMAGE=$(kubectl get pod $POD -n $KUBE_NAMESPACE -o json | jq ".spec.containers[0].image" | sed -e 's/^"//' | sed -e 's/"$//')
    POD_INFO_TABLE_OUT+="$POD $POD_IMAGE"
    POD_INFO_TABLE_OUT+=$'\n'
done

echo $"$POD_INFO_TABLE_OUT" | column -t > $NAMESPACE_POD_IMAGES_FILE