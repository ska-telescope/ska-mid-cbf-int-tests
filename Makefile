
PROJECT = ska-mid-cbf-int-tests

# WARNING:
# TODO: CIP-3061 Boolean strings used in this Makefile inconsistently behave
# depending on dev environment, specifically regarding trailing whitespace. Do
# not include trailing whitespace for any variables set as true or false. 

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
KUBE_NAMESPACE ?= ska-mid-cbf-int-tests
KUBE_NAMESPACE_SDP ?= $(KUBE_NAMESPACE)-sdp

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART ?= ska-mid-cbf-int-tests
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/

# RELEASE_NAME is the release that all Kubernetes resources will be labelled with
RELEASE_NAME = $(HELM_CHART)

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

# Chart for testing
K8S_CHART ?= $(HELM_CHART)
K8S_CHARTS ?= $(K8S_CHART)

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

CHART_FILE=charts/ska-mid-cbf-int-tests/Chart.yaml
VALUES_FILE=charts/ska-mid-cbf-int-tests/values.yaml
CAR_REGISTRY=artefact.skao.int
HELM_INTERNAL_REPO=https://${CAR_REGISTRY}/repository/helm-internal
MCS_HELM_REPO=https://gitlab.com/api/v4/projects/12488466/packages/helm/dev
SV_REGISTRY_REPO=registry.gitlab.com/ska-telescope/ska-mid-cbf-signal-verification
SV_CAR_REGISTRY=${CAR_REGISTRY}/ska-mid-cbf-signal-verification-visibility-capture
EC_HELM_REPO=https://gitlab.com/api/v4/projects/29657133/packages/helm/dev
EC_REGISTRY_REPO=registry.gitlab.com/ska-telescope/ska-mid-cbf-engineering-console
EC_CAR_REGISTRY=${CAR_REGISTRY}/ska-mid-cbf-engineering-console

FIND_MAIN_TAG_SCRIPT := $(abspath $(dir $(firstword $(MAKEFILE_LIST))))/scripts/find_latest_main_tag.sh

# Use Gitlab API to extract latest tags and builds from the main branch for MCS, to extract the hash versions
MCS_LATEST_COMMIT:=$(shell curl -s https://gitlab.com/api/v4/projects/12488466/repository/branches/main | jq -r '.commit.short_id')
MCS_LATEST_TAG:=$(shell $(FIND_MAIN_TAG_SCRIPT) 12488466)
MCS_HASH_VERSION?=$(MCS_LATEST_TAG)-dev.c$(MCS_LATEST_COMMIT)
# Use Gitlab API to extract latest tags and builds from the main branch for SV, to extract the hash versions
SV_LATEST_COMMIT:=$(shell curl -s https://gitlab.com/api/v4/projects/39434878/repository/branches/main | jq -r '.commit.short_id')
SV_LATEST_TAG:=$(shell $(FIND_MAIN_TAG_SCRIPT) 39434878)
SV_HASH_VERSION?=$(SV_LATEST_TAG)-dev.c$(SV_LATEST_COMMIT)
# Use Gitlab API to extract latest tags and builds from the main branch for EC, to extract the hash versions
EC_LATEST_COMMIT:=$(shell curl -s https://gitlab.com/api/v4/projects/29657133/repository/branches/main | jq -r '.commit.short_id')
EC_LATEST_TAG:=$(shell $(FIND_MAIN_TAG_SCRIPT) 29657133)
EC_HASH_VERSION?=$(EC_LATEST_TAG)-dev.c$(EC_LATEST_COMMIT)
# Use Gitlab API to extract latest tags and builds from the main branch for internal-schemas, to extract the hash versions
INTERNAL_SCHEMA_LATEST_COMMIT:=$(shell curl -s https://gitlab.com/api/v4/projects/47018613/repository/branches/main | jq -r .commit.short_id)
INTERNAL_SCHEMA_LATEST_TAG:=$(shell $(FIND_MAIN_TAG_SCRIPT) 47018613)
INTERNAL_SCHEMA_HASH_VERSION?=$(INTERNAL_SCHEMA_LATEST_TAG)+dev.c$(INTERNAL_SCHEMA_LATEST_COMMIT)
CURR_INTERNAL_SCHEMA_VERSION:=$(shell grep ska-mid-cbf-internal-schemas pyproject.toml | awk -F '"' '{print $$2}')


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
	--set ska-mid-cbf-tdc-mcs.hostInfo.clusterDomain=$(CLUSTER_DOMAIN) \
	--set global.labels.app=$(KUBE_APP) \
	$(TARANTA_PARAMS)

ifeq ($(SKA_TANGO_ARCHIVER),true)
	K8S_CHART_PARAMS += $(SKA_TANGO_ARCHIVER_PARAMS)
endif

USE_DEV_BUILD ?= true## Update the Chart.yaml and values.yaml for MCS, SV, and EC. If set to true, to use the latest tag versions from main branch on Gitlab

DEV_BUILD_PARAMS =  --set ska-mid-cbf-mcs.signalVerificationVersion=$(SV_HASH_VERSION) \
					--set ska-mid-cbf-mcs.midcbf.image.tag=$(MCS_HASH_VERSION) \
					--set ska-mid-cbf-tmleafnode.midcbf.image.tag=$(MCS_HASH_VERSION) \
					--set ska-mid-cbf-engineering-console.engineeringconsole.image.tag=$(EC_HASH_VERSION) \
					
TAG_BUILD_PARAMS =  --set ska-mid-cbf-mcs.signalVerificationVersion=$(SV_LATEST_TAG) \
					--set ska-mid-cbf-mcs.svImageRegistry=$(CAR_REGISTRY) \
					--set ska-mid-cbf-mcs.midcbf.image.tag=$(MCS_LATEST_TAG) \
					--set ska-mid-cbf-mcs.midcbf.image.registry=$(CAR_REGISTRY) \
					--set ska-mid-cbf-tmleafnode.midcbf.image.tag=$(MCS_LATEST_TAG) \
					--set ska-mid-cbf-tmleafnode.midcbf.image.registry=$(CAR_REGISTRY) \
					--set ska-mid-cbf-engineering-console.engineeringconsole.image.tag=$(EC_LATEST_TAG) \
					--set ska-mid-cbf-engineering-console.engineeringconsole.image.registry=$(CAR_REGISTRY) \

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

update-chart:
	@if [ "$(USE_DEV_BUILD)" == "false" ]; then \
		echo "Updating Chart.yaml to change ska-mid-cbf-mcs and ska-mid-cbf-tmleafnode version to $(MCS_LATEST_TAG) and repository to $(HELM_INTERNAL_REPO)"; \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-mcs").version) = "$(MCS_LATEST_TAG)"' $(CHART_FILE); \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-mcs").repository) = "$(HELM_INTERNAL_REPO)"' $(CHART_FILE); \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-tmleafnode").version) = "$(MCS_LATEST_TAG)"' $(CHART_FILE); \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-tmleafnode").repository) = "$(HELM_INTERNAL_REPO)"' $(CHART_FILE); \
		echo "Updating Chart.yaml to change ska-mid-cbf-engineering-console version to $(EC_LATEST_TAG) and repository to $(HELM_INTERNAL_REPO)"; \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-engineering-console").version) = "$(EC_LATEST_TAG)"' $(CHART_FILE); \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-engineering-console").repository) = "$(HELM_INTERNAL_REPO)"' $(CHART_FILE); \
	else \
		echo "Updating Chart.yaml to change ska-mid-cbf-mcs and ska-mid-cbf-tmleafnode version to $(MCS_HASH_VERSION) and repository to $(MCS_HELM_REPO)"; \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-mcs").version) = "$(MCS_HASH_VERSION)"' $(CHART_FILE); \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-mcs").repository) = "$(MCS_HELM_REPO)"' $(CHART_FILE); \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-tmleafnode").version) = "$(MCS_HASH_VERSION)"' $(CHART_FILE); \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-tmleafnode").repository) = "$(MCS_HELM_REPO)"' $(CHART_FILE); \
		echo "Updating values.yaml to change ska-mid-cbf-mcs and ska-mid-cbf-tmleafnode LRC timeout values; controllerTimeout: $(CONTROLLER_TIMEOUT)"; \
		yq eval -i '.ska-mid-cbf-tdc-mcs.controllerTimeout = $(CONTROLLER_TIMEOUT)' $(VALUES_FILE); \
		echo "Updating Chart.yaml to change ska-mid-cbf-engineering-console version to $(EC_HASH_VERSION) and repository to $(EC_HELM_REPO)"; \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-engineering-console").version) = "$(EC_HASH_VERSION)"' $(CHART_FILE); \
		yq eval -i '(.dependencies[] | select(.name == "ska-mid-cbf-engineering-console").repository) = "$(EC_HELM_REPO)"' $(CHART_FILE); \
	fi
	cat $(CHART_FILE)
	cat $(VALUES_FILE)

k8s-pre-install-chart:
	@echo "k8s-pre-install-chart: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
	make update-chart MCS_HASH_VERSION=$(MCS_HASH_VERSION) EC_HASH_VERSION=$(EC_HASH_VERSION)

k8s-pre-install-chart-car:
	@echo "k8s-pre-install-chart-car: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)

k8s-pre-uninstall-chart:
	@echo "k8s-post-uninstall-chart: deleting the SDP namespace $(KUBE_NAMESPACE_SDP)"
	@if [ "$(KEEP_NAMESPACE)" != "true" ]; then make k8s-delete-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP); fi

python-pre-test:
	@echo "Update dish_packet_capture_$(TARGET_SITE).yaml using ENGINEERING_CONSOLE_IMAGE_VER set to $(ENGINEERING_CONSOLE_IMAGE_VER)"
	@if [ "$(USE_DEV_BUILD)" == "false" ]; then \
		echo "and image set to $(EC_CAR_REGISTRY)"; \
		cat charts/ska-mid-cbf-int-tests/resources/dish_packet_capture_$(TARGET_SITE).yaml | sed -e "s|${EC_REGISTRY_REPO}/ska-mid-cbf-engineering-console|${EC_CAR_REGISTRY}|" -e "s|ENGINEERING_CONSOLE_IMAGE_VER|${ENGINEERING_CONSOLE_IMAGE_VER}|" > dish_packet_capture_temp.yaml; \
	else \
		cat charts/ska-mid-cbf-int-tests/resources/dish_packet_capture_$(TARGET_SITE).yaml | sed -e "s|ENGINEERING_CONSOLE_IMAGE_VER|${ENGINEERING_CONSOLE_IMAGE_VER}|" > dish_packet_capture_temp.yaml; \
	fi
	cat dish_packet_capture_temp.yaml
	@echo "Update visibilities_pod_$(TARGET_SITE).yaml using SIGNAL_VERIFICATION_IMAGE_VER set to $(SIGNAL_VERIFICATION_IMAGE_VER)"
	@if [ "$(USE_DEV_BUILD)" == "false" ]; then \
		echo "and image set to $(SV_CAR_REGISTRY)"; \
		cat charts/ska-mid-cbf-int-tests/resources/visibilities_pod_$(TARGET_SITE).yaml | sed -e "s|${SV_REGISTRY_REPO}/ska-mid-cbf-signal-verification-visibility-capture|${SV_CAR_REGISTRY}|" -e "s|SIGNAL_VERIFICATION_IMAGE_VER|${SIGNAL_VERIFICATION_IMAGE_VER}|" > visibilities_pod_temp.yaml; \
	else \
		cat charts/ska-mid-cbf-int-tests/resources/visibilities_pod_$(TARGET_SITE).yaml | sed -e "s|SIGNAL_VERIFICATION_IMAGE_VER|${SIGNAL_VERIFICATION_IMAGE_VER}|" > visibilities_pod_temp.yaml; \
	fi
	cat visibilities_pod_temp.yaml
	make update-internal-schema
	poetry show ska-mid-cbf-internal-schemas > build/reports/internal_schemas_version.txt
	cat build/reports/internal_schemas_version.txt | grep version

python-post-test:
	rm dish_packet_capture_temp.yaml
	rm visibilities_pod_temp.yaml

run-pylint:
	pylint --output-format=parseable notebooks/ tests/ test_parameters/ | tee build/code_analysis.stdout

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
