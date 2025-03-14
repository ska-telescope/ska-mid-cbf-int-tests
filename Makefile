
PROJECT = ska-mid-cbf-int-tests

# WARNING:
# TODO: CIP-3061 Boolean strings used in this Makefile inconsistently behave
# depending on dev environment, specifically regarding trailing whitespace. Do
# not include trailing whitespace for any variables set as true or false. 

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
KUBE_NAMESPACE ?= ska-mid-cbf-int-tests

KUBE_APP ?= ska-mid-cbf-int-tests

TARANTA ?= true## Enable Taranta
TARANTA_AUTH ?= false## Enable Taranta

EXPOSE_All_DS ?= true## Expose All Tango Services to the external network (enable Loadbalancer service)
SKA_TANGO_OPERATOR ?= true
SKA_TANGO_ARCHIVER ?= false## Set to true to deploy EDA

TARGET_SITE ?= psi

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

# include core make support
include .make/base.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak

TARANTA_PARAMS = --set ska-taranta.enabled=$(TARANTA) \
				 --set global.taranta_auth_enabled=$(TARANTA_AUTH) \
				 --set global.taranta_dashboard_enabled=$(TARANTA)
endif
endif

CI_JOB_ID ?= local##pipeline job id
TANGO_HOST ?= databaseds-tango-base:10000## TANGO_HOST connection to the Tango DS
CLUSTER_DOMAIN ?= cluster.local## Domain used for naming Tango Device Servers

ENGINEERING_CONSOLE_IMAGE_VER=$(shell kubectl describe pod/ds-deployer-deployer-0 -n $(KUBE_NAMESPACE) | grep 'Image:' | sed 's/.*\://')
SIGNAL_VERIFICATION_IMAGE_VER=$(shell kubectl describe pod/sv -n $(KUBE_NAMESPACE) | grep ska-mid-cbf-signal-verification | grep 'Image:' | sed 's/.*\://')


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

ifeq ($(USE_DEV_BUILD),true)
	K8S_CHART_PARAMS += $(DEV_BUILD_PARAMS)
else ifeq ($(USE_DEV_BUILD),false)
	K8S_CHART_PARAMS += $(TAG_BUILD_PARAMS)
endif

ifneq (,$(wildcard $(VALUES)))
	K8S_CHART_PARAMS += $(foreach f,$(wildcard $(VALUES)),--values $(f))
endif

# MCS timeout values in seconds
CONTROLLER_TIMEOUT?=100

echo-charts:
	@echo $(K8S_CHART_PARAMS)

# TODO: the target for pylint should be specified when the repo is more developed
# run-pylint:
# 	pylint --output-format=parseable notebooks/ tests/ test_parameters/ | tee build/code_analysis.stdout

vars:
	$(info ##### Mid deploy vars)
	@echo "$(VARS)" | sed "s#VAR_#\n#g"

