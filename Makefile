
PROJECT = ska-mid-cbf-int-tests

# WARNING:
# TODO: CIP-3061 Boolean strings used in this Makefile inconsistently behave
# depending on dev environment, specifically regarding trailing whitespace. Do
# not include trailing whitespace for any variables set as true or false. 

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
KUBE_NAMESPACE ?= ska-mid-cbf-int-tests
KUBE_NAMESPACE_SDP ?= $(KUBE_NAMESPACE)-sdp

KUBE_APP ?= ska-mid-cbf-int-tests

TARANTA ?= true## Enable Taranta
TARANTA_AUTH ?= false## Enable Taranta
MINIKUBE ?= false## Minikube or not

LOADBALANCER_IP ?= 142.73.34.170## psi mid head node
INGRESS_PROTOCOL ?= https
ifeq ($(strip $(MINIKUBE)),true)
LOADBALANCER_IP ?= $(shell minikube ip)
INGRESS_HOST ?= $(LOADBALANCER_IP)
INGRESS_PROTOCOL ?= http
endif

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

ifneq ($(MINIKUBE),)
ifneq ($(MINIKUBE),true)
TARANTA_PARAMS = --set ska-taranta.enabled=$(TARANTA) \
				 --set global.taranta_auth_enabled=$(TARANTA_AUTH) \
				 --set global.taranta_dashboard_enabled=$(TARANTA)
endif
endif

CI_JOB_ID ?= local##pipeline job id
TANGO_HOST ?= databaseds-tango-base:10000## TANGO_HOST connection to the Tango DS
CLUSTER_DOMAIN ?= cluster.local## Domain used for naming Tango Device Servers

# TODO: the python lint target and error codes that are disabled/ignored should be updated as the repo evolves  
PYTHON_SWITCHES_FOR_FLAKE8 = --ignore=E501,F407,W503,D100,D103,D400,DAR101,D104,D101,D107,D401,FS002,D200,DAR201,D202,D403,N802,DAR401,E203
PYTHON_SWITCHES_FOR_PYLINT = --disable=W0613,C0116,C0114,R0801,W0621,W1203,C0301,F0010,R1721,R1732,C2801,C0115,R0903,W0102,W0201,C0103
# PYTHON_LINT_TARGET = ./

ENGINEERING_CONSOLE_IMAGE_VER=$(shell kubectl describe pod/ds-deployer-deployer-0 -n $(KUBE_NAMESPACE) | grep 'Image:' | sed 's/.*\://')
SIGNAL_VERIFICATION_IMAGE_VER=$(shell kubectl describe pod/sv -n $(KUBE_NAMESPACE) | grep ska-mid-cbf-signal-verification | grep 'Image:' | sed 's/.*\://')


K8S_EXTRA_PARAMS ?=
K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) \
	--set global.exposeAllDS=$(EXPOSE_All_DS) \
	--set global.tango_host=$(TANGO_HOST) \
	--set global.cluster_domain=$(CLUSTER_DOMAIN) \
	--set global.operator=$(SKA_TANGO_OPERATOR) \
	--set ska-sdp.helmdeploy.namespace=$(KUBE_NAMESPACE_SDP) \
	--set ska-sdp.ska-sdp-qa.zookeeper.clusterDomain=$(CLUSTER_DOMAIN) \
	--set ska-sdp.ska-sdp-qa.kafka.clusterDomain=$(CLUSTER_DOMAIN) \
	--set ska-sdp.ska-sdp-qa.redis.clusterDomain=$(CLUSTER_DOMAIN) \
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

echo-internal-schema:
	@echo "INTERNAL_SCHEMA_LATEST_TAG = $(INTERNAL_SCHEMA_LATEST_TAG)"
	@echo "INTERNAL_SCHEMA_LATEST_COMMIT = $(INTERNAL_SCHEMA_LATEST_COMMIT)"
	@echo "INTERNAL_SCHEMA_HASH_VERSION = $(INTERNAL_SCHEMA_HASH_VERSION)"
	@echo "CURR_INTERNAL_SCHEMA_VERSION = $(CURR_INTERNAL_SCHEMA_VERSION)"

update-internal-schema:
	@if [ "$(USE_DEV_BUILD)" == "false" ]; then \
		echo "$(CURR_INTERNAL_SCHEMA_VERSION)"; \
		echo "Update ska-mid-cbf-internal-schemas source in pyproject.toml to use nexus-internal"; \
		sed -i '/ska-mid-cbf-internal-schemas/ s/version = "$(CURR_INTERNAL_SCHEMA_VERSION)"/version = "$(INTERNAL_SCHEMA_LATEST_TAG)"/' pyproject.toml; \
		sed -i '/ska-mid-cbf-internal-schemas/ s/source = "gitlab-internal-schemas"/source = "nexus-internal"/' pyproject.toml; \
		cat pyproject.toml; \
		poetry update ska-mid-cbf-internal-schemas; \
	elif [ "$(USE_DEV_BUILD)"  == "true" ] && [ $(CURR_INTERNAL_SCHEMA_VERSION) != $(INTERNAL_SCHEMA_HASH_VERSION) ]; then \
		echo "Update ska-mid-cbf-internal-schemas version in pyproject.toml to use $(INTERNAL_SCHEMA_HASH_VERSION)"; \
		sed -i '/ska-mid-cbf-internal-schemas/ s/version = "$(CURR_INTERNAL_SCHEMA_VERSION)"/version = "$(INTERNAL_SCHEMA_HASH_VERSION)"/' pyproject.toml; \
		cat pyproject.toml; \
		poetry update ska-mid-cbf-internal-schemas; \
	else \
		echo "No changes needed to pyproject.toml for ska-mid-cbf-internal-schemas"; \
	fi

k8s-pre-install-chart:
	@echo "k8s-pre-install-chart: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)

k8s-pre-install-chart-car:
	@echo "k8s-pre-install-chart-car: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)

k8s-pre-uninstall-chart:
	@echo "k8s-post-uninstall-chart: deleting the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@if [ "$(KEEP_NAMESPACE)" != "true" ]; then make k8s-delete-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP); fi

# TODO: the target for pylint should be specified when the repo is more developed
# run-pylint:
# 	pylint --output-format=parseable notebooks/ tests/ test_parameters/ | tee build/code_analysis.stdout

vars:
	$(info ##### Mid deploy vars)
	@echo "$(VARS)" | sed "s#VAR_#\n#g"

links:
	@echo ${CI_JOB_NAME}
	@echo "############################################################################"
	@echo "#            Access the Skampi landing page here:"
	@echo "#            $(INGRESS_PROTOCOL)://$(INGRESS_HOST)/$(KUBE_NAMESPACE)/start/"
	@echo "#     NOTE: Above link will only work if you can reach $(INGRESS_HOST)"
	@echo "############################################################################"
	@if [[ -z "${LOADBALANCER_IP}" ]]; then \
		exit 0; \
	elif [[ $(shell curl -I -s -o /dev/null -I -w \'%{http_code}\' http$(S)://$(LOADBALANCER_IP)/$(KUBE_NAMESPACE)/start/) != '200' ]]; then \
		echo "ERROR: http://$(LOADBALANCER_IP)/$(KUBE_NAMESPACE)/start/ unreachable"; \
		exit 10; \
	fi
