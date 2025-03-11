#!/bin/bash

RESULTS_DIR=$1

CI_PIPELINE_ID=$2
CI_JOB_ID=$3

CI_JOB_STARTED_AT=$4
CI_PIPELINE_CREATED_AT=$5

CI_JOB_URL=$6
CI_PIPELINE_URL=$7

VISIBILITIES_COPIED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

PVC_NAMESPACE="system-tests-artifacts"
PVC_POD="artifacts-sts-0"
PVC_POD_NETWORK_PATH="$PVC_NAMESPACE/$PVC_POD"

PVC_VIS_DIR="app/artifacts/pline_"$CI_PIPELINE_ID"_job_"$CI_JOB_ID"_visibilities"
PVC_VIS_DIR_NETWORK_PATH="$PVC_POD_NETWORK_PATH:$PVC_VIS_DIR"

VISIBILITY_ARTIFACT_PATH_TXT_FNAME="visibility_artifact_path.txt"
echo "Save path $PVC_VIS_DIR_NETWORK_PATH to $VISIBILITY_ARTIFACT_PATH_TXT_FNAME"
echo $PVC_VIS_DIR_NETWORK_PATH > $VISIBILITY_ARTIFACT_PATH_TXT_FNAME

echo "Saving visibilities into $PVC_VIS_DIR_NETWORK_PATH"
kubectl exec $PVC_POD -n $PVC_NAMESPACE -- mkdir -p $PVC_VIS_DIR

TEST_DIRS=$(ls $RESULTS_DIR | grep Test_)

for TEST_DIR in $TEST_DIRS; do
    LOCAL_TEST_DIR_VIS_PATH=$RESULTS_DIR/$TEST_DIR/visibilities
    if [ -d $LOCAL_TEST_DIR_VIS_PATH ]; then
        PVC_TEST_DIR_VIS_PATH=$PVC_VIS_DIR/$TEST_DIR/visibilities
        PVC_TEST_DIR_VIS_NETWORK_PATH="$PVC_POD_NETWORK_PATH:$PVC_TEST_DIR_VIS_PATH"
        echo "$LOCAL_TEST_DIR_VIS_PATH/* to $PVC_TEST_DIR_VIS_NETWORK_PATH"
        kubectl exec $PVC_POD -n $PVC_NAMESPACE -- mkdir -p $PVC_TEST_DIR_VIS_PATH
        kubectl cp $LOCAL_TEST_DIR_VIS_PATH/* $PVC_TEST_DIR_VIS_NETWORK_PATH
    fi
done

PVC_METADATA_JSON_FNAME="metadata.json"
PVC_METADATA_NETWORK_PATH="$PVC_VIS_DIR_NETWORK_PATH/$PVC_METADATA_JSON_FNAME"

echo "Saving metadata at $PVC_METADATA_NETWORK_PATH"

JSON_STRING="{\
\"visibilities_copied_at\":\"$VISIBILITIES_COPIED_AT\",\
\"ci_job_started_at\":\"$CI_JOB_STARTED_AT\",\
\"ci_pipeline_created_at\":\"$CI_PIPELINE_CREATED_AT\",\
\"ci_job_url\":\"$CI_JOB_URL\",\
\"ci_pipeline_url\":\"$CI_PIPELINE_URL\"\
}"
echo "Metadata: "$JSON_STRING
echo $JSON_STRING > $PVC_METADATA_JSON_FNAME

kubectl cp "./$PVC_METADATA_JSON_FNAME" $PVC_METADATA_NETWORK_PATH

echo "PVC Space Check:"
ABS_SCRIPT_DIR_PATH=$(dirname "$0")
sh -c "$ABS_SCRIPT_DIR_PATH/check_pvc_space.sh"

exit 0