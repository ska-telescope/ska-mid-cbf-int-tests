HELM_CHART_FILE = $(MAKEFILE_ROOT_DIR)/charts/ska-mid-cbf-int-tests/Chart.yaml
HELM_VALUES_FILE = $(MAKEFILE_ROOT_DIR)/charts/ska-mid-cbf-int-tests/values.yaml

MCS_CHART_NAME = ska-mid-cbf-mcs
MCS_TMLEAFNODE_CHART_NAME = ska-mid-cbf-tmleafnode
MCS_DEV_HELM_REPO = https://gitlab.com/api/v4/projects/$(MCS_PROJECT_ID)/packages/helm/dev
MCS_DEV_IMAGE_REPO = registry.gitlab.com/ska-telescope/$(MCS_CHART_NAME)

EC_CHART_NAME = ska-mid-cbf-engineering-console
EC_DEV_HELM_REPO = https://gitlab.com/api/v4/projects/$(EC_PROJECT_ID)/packages/helm/dev
EC_DEV_IMAGE_REPO = registry.gitlab.com/ska-telescope/$(EC_CHART_NAME)

update-cbf-charts-to-dev-hash:
	echo "Updating charts $(MCS_CHART_NAME) hash: $(MCS_DEV_HASH_VERSION), repository: $(MCS_DEV_HELM_REPO), registry: $(MCS_DEV_IMAGE_REPO)"
	yq eval -i '(.dependencies[] | select(.name == "$(MCS_CHART_NAME)").version) = "$(MCS_DEV_HASH_VERSION)"' $(HELM_CHART_FILE)
	yq eval -i '(.dependencies[] | select(.name == "$(MCS_CHART_NAME)").repository) = "$(MCS_DEV_HELM_REPO)"' $(HELM_CHART_FILE)
	yq eval -i '(.$(MCS_CHART_NAME).midcbf.image.tag) = "$(MCS_DEV_HASH_VERSION)"' $(HELM_VALUES_FILE)
	yq eval -i '(.$(MCS_CHART_NAME).midcbf.image.registry) = "$(MCS_DEV_IMAGE_REPO)"' $(HELM_VALUES_FILE)

	echo "Updating charts $(MCS_TMLEAFNODE_CHART_NAME) hash: $(MCS_DEV_HASH_VERSION), repository: $(MCS_DEV_HELM_REPO), registry: $(MCS_DEV_IMAGE_REPO)"
	yq eval -i '(.dependencies[] | select(.name == "$(MCS_TMLEAFNODE_CHART_NAME)").version) = "$(MCS_DEV_HASH_VERSION)"' $(HELM_CHART_FILE)
	yq eval -i '(.dependencies[] | select(.name == "$(MCS_TMLEAFNODE_CHART_NAME)").repository) = "$(MCS_DEV_HELM_REPO)"' $(HELM_CHART_FILE)
	yq eval -i '(.$(MCS_TMLEAFNODE_CHART_NAME).midcbf.image.tag) = "$(MCS_DEV_HASH_VERSION)"' $(HELM_VALUES_FILE)
	yq eval -i '(.$(MCS_TMLEAFNODE_CHART_NAME).midcbf.image.registry) = "$(MCS_DEV_IMAGE_REPO)"' $(HELM_VALUES_FILE)

	echo "Updating charts $(EC_CHART_NAME) hash: $(EC_DEV_HASH_VERSION), repository: $(EC_DEV_HELM_REPO), registry: $(EC_DEV_IMAGE_REPO)"
	yq eval -i '(.dependencies[] | select(.name == "$(EC_CHART_NAME)").version) = "$(EC_DEV_HASH_VERSION)"' $(HELM_CHART_FILE)
	yq eval -i '(.dependencies[] | select(.name == "$(EC_CHART_NAME)").repository) = "$(EC_DEV_HELM_REPO)"' $(HELM_CHART_FILE)
	yq eval -i '(.$(EC_CHART_NAME).engineeringconsole.image.tag) = "$(EC_DEV_HASH_VERSION)"' $(HELM_VALUES_FILE)
	yq eval -i '(.$(EC_CHART_NAME).engineeringconsole.image.registry) = "$(EC_DEV_IMAGE_REPO)"' $(HELM_VALUES_FILE)