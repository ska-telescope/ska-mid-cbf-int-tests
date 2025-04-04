
PROJECT = ska-mid-cbf-int-tests

# WARNING:
# TODO: CIP-3061 Boolean strings used in this Makefile inconsistently behave
# depending on dev environment, specifically regarding trailing whitespace. Do
# not include trailing whitespace for any variables set as true or false. 

KUBE_NAMESPACE ?=

KUBE_APP ?= ska-mid-cbf-int-tests

# Enable Taranta
TARANTA ?= true
TARANTA_AUTH ?= false

EXPOSE_All_DS ?= true## Expose All Tango Services to the external network (enable Loadbalancer service)
SKA_TANGO_OPERATOR ?= true
SKA_TANGO_ARCHIVER ?= false## Set to true to deploy EDA

TARGET_SITE ?= psi

# include core make support
include .make/base.mk

# include OCI Images support
include .make/oci.mk

# include k8s support
include .make/k8s.mk

# include Helm Chart support
include .make/helm.mk

# Include Python support
include .make/python.mk

# include raw support
include .make/raw.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak

PYTEST_MARKER ?= default

# 1 for assertions in test 0 for no assertions
ALO_ASSERTING ?= 1

CI_JOB_ID ?= local##pipeline job id
TANGO_HOST ?= databaseds-tango-base:10000## Tango DB DNS address on namespace
CLUSTER_DOMAIN ?= cluster.local## DNS cluster name

TARANTA_PARAMS = --set ska-taranta.enabled=$(TARANTA) \
	--set global.taranta_auth_enabled=$(TARANTA_AUTH) \
	--set global.taranta_dashboard_enabled=$(TARANTA)

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

# MCS timeout values in seconds
CONTROLLER_TIMEOUT?=100

PYTHON_VARS_AFTER_PYTEST = \
	-m $(PYTEST_MARKER) \
	-v -s \
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

# Quickly fix isort lint issues
python-fix-isort:
	$(PYTHON_RUNNER) isort --profile black --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(PYTHON_LINT_TARGET)

# Quickly fix black line issues
python-fix-black:
	$(PYTHON_RUNNER) black --exclude .+\.ipynb --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(PYTHON_LINT_TARGET)

# IMPORTANT: include a justification if adding something to the list
# lint exception: missing-module-docstring markdown cells acting as better
#                 formatted docstrings for notebooks cover this
NOTEBOOK_SWITCHES_FOR_PYLINT = --disable=missing-module-docstring

# Quickly fix notebook isort lint issues
notebook-fix-isort:
	$(PYTHON_RUNNER) nbqa isort --profile=black --line-length=$(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(NOTEBOOK_SWITCHES_FOR_ISORT) $(NOTEBOOK_LINT_TARGET)

# Quickly fix notebook black line issues
notebook-fix-black:
	$(PYTHON_RUNNER) nbqa black --line-length=$(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(NOTEBOOK_SWITCHES_FOR_BLACK) $(NOTEBOOK_LINT_TARGET)

echo-charts:
	@echo $(K8S_CHART_PARAMS)

vars:
	$(info ##### Mid deploy vars)
	@echo "$(VARS)" | sed "s#VAR_#\n#g"

