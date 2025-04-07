#!/bin/bash

# Retrieve latest commit hash from the given Gitlab project ID
# param $1: Gitlab project ID to get commit hash for

GITLAB_PROJECT_ID=$1

TAG_LINE=$(curl -s https://gitlab.com/api/v4/projects/$GITLAB_PROJECT_ID/repository/files/.release/raw?ref=main | grep "tag")
IFS="=" read TAG_KEY TAG <<< $(echo $TAG_LINE)

COMMIT=$(curl -s https://gitlab.com/api/v4/projects/$GITLAB_PROJECT_ID/repository/branches/main | jq -r '.commit.short_id')

if [ -z $TAG ] || [ -z $COMMIT ]; then # Check empty
    exit 1;
else
    echo "$TAG-dev.c$COMMIT";
fi