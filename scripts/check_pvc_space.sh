#!/bin/bash

kubectl exec artifacts-sts-0 -n int-tests-artifacts -- df -ah /app/artifacts/