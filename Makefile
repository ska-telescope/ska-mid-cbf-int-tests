
PROJECT = ska-mid-cbf-int-tests

include .make/base.mk
include .make/k8s.mk
include .make/helm.mk
include .make/oci.mk
include .make/python.mk

MAKEFILE_ROOT_DIR := $(abspath $(dir $(firstword $(MAKEFILE_LIST))))
SCRIPT_DIR := $(MAKEFILE_ROOT_DIR)/scripts

# WARNING:
# TODO: CIP-3061 Boolean strings used in this Makefile inconsistently behave
# depending on dev environment, specifically regarding trailing whitespace. Do
# not include trailing whitespace for any variables set as true or false. 

KUBE_APP ?= ska-mid-cbf-int-tests
KUBE_NAMESPACE ?=

# Enable Taranta
TARANTA ?= true
TARANTA_AUTH ?= false

EXPOSE_All_DS ?= true## Expose All Tango Services to the external network (enable Loadbalancer service)
SKA_TANGO_OPERATOR ?= true
SKA_TANGO_ARCHIVER ?= false## Set to true to deploy EDA

TARGET_SITE ?= psi

TARANTA_PARAMS = --set ska-taranta.enabled=$(TARANTA) \
	--set global.taranta_auth_enabled=$(TARANTA_AUTH) \
	--set global.taranta_dashboard_enabled=$(TARANTA)

CI_JOB_ID ?= local##pipeline job id
TANGO_HOST ?= databaseds-tango-base:10000## Tango DB DNS address on namespace
CLUSTER_DOMAIN ?= cluster.local## DNS cluster name

# MCS timeout values in seconds
CONTROLLER_TIMEOUT ?= 100

K8S_EXTRA_PARAMS ?=
K8S_CHART_PARAMS = --set global.exposeAllDS=$(EXPOSE_All_DS) \
	--set global.tango_host=$(TANGO_HOST) \
	--set global.cluster_domain=$(CLUSTER_DOMAIN) \
	--set global.operator=$(SKA_TANGO_OPERATOR) \
	--set ska-mid-cbf-mcs.hostInfo.clusterDomain=$(CLUSTER_DOMAIN) \
	--set global.labels.app=$(KUBE_APP) \
	$(TARANTA_PARAMS)
ifeq ($(SKA_TANGO_ARCHIVER),true)
	K8S_CHART_PARAMS += $(SKA_TANGO_ARCHIVER_PARAMS)
endif

CHART_FILE = $(MAKEFILE_ROOT_DIR)/charts/ska-mid-cbf-int-tests/Chart.yaml
VALUES_FILE = $(MAKEFILE_ROOT_DIR)/charts/ska-mid-cbf-int-tests/values.yaml

MCS_CHART_NAME = ska-mid-cbf-mcs
MCS_TMLEAFNODE_CHART_NAME = ska-mid-cbf-tmleafnode
MCS_PROJECT_ID = 12488466
MCS_DEV_HELM_REPO = https://gitlab.com/api/v4/projects/$(MCS_PROJECT_ID)/packages/helm/dev
MCS_DEV_IMAGE_REPO = registry.gitlab.com/ska-telescope/$(MCS_CHART_NAME)
MCS_LATEST_HASH_VERSION ?= $(shell $(SCRIPT_DIR)/charts/get_latest_hash.sh $(MCS_PROJECT_ID))

EC_CHART_NAME = ska-mid-cbf-engineering-console
EC_PROJECT_ID = 29657133
EC_DEV_HELM_REPO = https://gitlab.com/api/v4/projects/$(EC_PROJECT_ID)/packages/helm/dev
EC_DEV_IMAGE_REPO = registry.gitlab.com/ska-telescope/$(EC_CHART_NAME)
EC_LATEST_HASH_VERSION ?= $(shell $(SCRIPT_DIR)/charts/get_latest_hash.sh $(EC_PROJECT_ID))

# Whether to update to latest Mid.CBF charts to latest hash or not
USE_DEV_HASH ?= true

# include int-tests chart update Make functions
include scripts/charts/cbf-chart-update.mk

echo-charts:
	@echo $(K8S_CHART_PARAMS)

PYTEST_MARKER ?= default
ALO_ASSERTING ?= 1## 1 for assertions in test 0 for no assertions

PYTHON_VARS_AFTER_PYTEST = \
	-m $(PYTEST_MARKER) \
	-v \
	--capture=no \
	--log-cli-level=INFO \
	--alo-asserting $(ALO_ASSERTING) \
	--namespace-tango-db-address $(TANGO_HOST) \
	--kube-namespace $(KUBE_NAMESPACE) \
	--kube-cluster-domain $(CLUSTER_DOMAIN)

PYTHON_LINT_TARGET = src tests/ notebooks/
# IMPORTANT: include a justification if adding something to the list
# lint exception: redefined-outer-name must be disabled for pytest fixtures
# lint exception: unused-argument must be disabled for pytest fixtures
# lint exception: attribute-defined-outside-init must be disabled to satisfy
#     pytest requirement of not collecting test classes with __init__ while
#     still being able to use class instance attributes
PYTHON_SWITCHES_FOR_PYLINT = --disable=redefined-outer-name,unused-argument,attribute-defined-outside-init

# IMPORTANT: include a justification if adding something to the list
# lint exception: missing-module-docstring markdown cells acting as better
#                 formatted docstrings for notebooks cover this
NOTEBOOK_SWITCHES_FOR_PYLINT = --disable=missing-module-docstring

# include int-tests lint helper Make functions
include scripts/lint/lint-helper.mk