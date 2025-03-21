
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

PYTEST_MARKER ?=
ALO_ASSERTING ?= 1

CI_JOB_ID ?= local##pipeline job id
TANGO_HOST ?= databaseds-tango-base:10000## TANGO_HOST connection to the Tango DS
CLUSTER_DOMAIN ?= cluster.local## Domain used for naming Tango Device Servers

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

# Add verbosity and INFO logging to python-test
PYTHON_VARS_AFTER_PYTEST = -v \
    --capture=no \
	--log-cli-level=INFO \
	--alo-asserting $(ALO_ASSERTING) \
	--namespace $(KUBE_NAMESPACE) \
	--cluster-domain $(CLUSTER_DOMAIN) \
	--tango-host $(TANGO_HOST)

# lint exception: redefined-outer-name must be disabled for pytest fixtures
# lint exception: unused-argument must be disabled for pytest fixtures
# lint exception: attribute-defined-outside-init must be disabled to satisfy
#     pytest requirement of not collecting test classes with __init__ while
#     using attributes
PYTHON_SWITCHES_FOR_PYLINT = --disable=redefined-outer-name,unused-argument,attribute-defined-outside-init
PYTHON_LINT_TARGET = src tests/ notebooks/

# Quickly fix isort lint issues
python-fix-isort:
	$(PYTHON_RUNNER) isort --profile black --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(PYTHON_LINT_TARGET)

# Quickly fix black line issues
python-fix-black:
	$(PYTHON_RUNNER) black --exclude .+\.ipynb --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(PYTHON_LINT_TARGET)

echo-charts:
	@echo $(K8S_CHART_PARAMS)

# TODO: the target for pylint should be specified when the repo is more developed
# run-pylint:
# 	pylint --output-format=parseable notebooks/ tests/ test_parameters/ | tee build/code_analysis.stdout

vars:
	$(info ##### Mid deploy vars)
	@echo "$(VARS)" | sed "s#VAR_#\n#g"

