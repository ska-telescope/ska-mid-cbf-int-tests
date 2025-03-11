#!/bin/bash

# Script to clean up the system-tests artifacts PVC of folders older than N days
# This script will be copied to the PSI worker node rmdskadevdu012 /home/user/maint/bin directory
# A cronjob will be created to run this script weekly and save the output to a log file
# The log file will be located on /home/user/maint/logs
#
# Usage:
# ./cleanup_artifacts.sh [N]
#
# where N is a postive integer number of days greater than 7
# if N is not provided, then the DEFAULT_DAYS_OLD value of 14 is used

# Default number of days old, if not provided otherwise
DEFAULT_DAYS_OLD=14

NAMESPACE="system-tests-artifacts"
POD_NAME="artifacts-sts-0"
ARTIFACTS_FOLDER="/app/artifacts"

FORMAT='+%Y-%m-%d %H:%M:%S'

# Check if number of days old is provided as a command line argument
if [ -z "$1" ]; then
    DAYS_OLD=$DEFAULT_DAYS_OLD
else
    DAYS_OLD=$1
fi

# Ensure DAYS_OLD is postive number and greater than 7 (to prevent accidental deletion of everything)
if [ "$DAYS_OLD" -le 7 ]; then
    echo "$(date "$FORMAT") - ERROR: Number of days must be greater than 7 (to prevent accidentaly delection of everything)."
    exit 1
fi

FIND_CMD="find $ARTIFACTS_FOLDER -type d -mtime +$DAYS_OLD -maxdepth 1"

echo "========================================================================================="
echo "$(date "$FORMAT") - Executing cleanup command on folders older than $DAYS_OLD days old..."

OLD_DIRECTORIES=$(kubectl exec -n "$NAMESPACE" "$POD_NAME" -- bash -c "$FIND_CMD")

# Check if any directories older than $DAYS_OLD are found
if [ -z "$OLD_DIRECTORIES" ]; then  
    echo "$(date "$FORMAT") - Nothing to delete"
else
    echo -e "$(date "$FORMAT") - Deleting...\n"
    echo "$OLD_DIRECTORIES"
    kubectl exec -n "$NAMESPACE" "$POD_NAME" -- bash -c "$FIND_CMD -exec rm -rf {} +"
    echo ""

    # Check if the deletion was successful
    if [ $? -eq 0 ]; then
        echo "$(date "$FORMAT") - Cleanup completed successfully"
    else
        echo "$(date "$FORMAT") - ERROR: An error occurred during the cleanup process."
    fi
fi
