#!/bin/bash

kubectl exec artifacts-sts-0 -n system-tests-artifacts -- df -ah /app/artifacts/