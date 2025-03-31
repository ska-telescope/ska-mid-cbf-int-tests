#!/bin/bash

# Clear metadata and outputs from all notebooks in the ../notebooks dir

NOTEBOOKS_DIR="$(dirname "$0")/../notebooks"

TARGET_IPYNBS=$(find $NOTEBOOKS_DIR -name "*.ipynb")

jupyter-nbconvert $TARGET_IPYNBS --to=notebook --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --log-level=INFO

# Extract original names from cleared new notebooks to ensure that
# if any failed to clear they are not deleted.
CLEARED_IPYNBS=$(find $NOTEBOOKS_DIR -name "*.nbconvert.ipynb")
ORIG_IPYNBS="${CLEARED_IPYNBS//\.nbconvert/}"

CLEARED_ARR=($CLEARED_IPYNBS)
ORIG_ARR=($ORIG_IPYNBS)

for index in ${!CLEARED_ARR[@]}; do
    mv "${CLEARED_ARR[$index]}" "${ORIG_ARR[$index]}"
done