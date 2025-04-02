update-cbf-charts-to-latest-dev:
	echo "Updating Chart.yaml to change $(MCS_CHART_NAME) to $(MCS_LATEST_HASH_VERSION) and repository to $(MCS_DEV_HELM_REPO)"
	yq eval -i '(.dependencies[] | select(.name == "$(MCS_CHART_NAME)").version) = "$(MCS_LATEST_HASH_VERSION)"' $(CHART_FILE)
	yq eval -i '(.dependencies[] | select(.name == "$(MCS_CHART_NAME)").repository) = "$(MCS_DEV_HELM_REPO)"' $(CHART_FILE)

	echo "Updating values.yaml to change $(MCS_CHART_NAME) to $(MCS_LATEST_HASH_VERSION) and registry to $(MCS_DEV_IMAGE_REPO)"
	yq eval -i '(.$(MCS_CHART_NAME).midcbf.image.tag) = "$(MCS_LATEST_HASH_VERSION)"' $(VALUES_FILE)
	yq eval -i '(.$(MCS_CHART_NAME).midcbf.image.registry) = "$(MCS_DEV_IMAGE_REPO)"' $(VALUES_FILE)

	echo "Updating Chart.yaml to change $(MCS_TMLEAFNODE_CHART_NAME) to $(MCS_LATEST_HASH_VERSION) and repository to $(MCS_DEV_HELM_REPO)"
	yq eval -i '(.dependencies[] | select(.name == "$(MCS_TMLEAFNODE_CHART_NAME)").version) = "$(MCS_LATEST_HASH_VERSION)"' $(CHART_FILE)
	yq eval -i '(.dependencies[] | select(.name == "$(MCS_TMLEAFNODE_CHART_NAME)").repository) = "$(MCS_DEV_HELM_REPO)"' $(CHART_FILE)

	echo "Updating values.yaml to change $(MCS_TMLEAFNODE_CHART_NAME) to $(MCS_LATEST_HASH_VERSION) and registry to $(MCS_DEV_IMAGE_REPO)"
	yq eval -i '(.$(MCS_TMLEAFNODE_CHART_NAME).midcbf.image.tag) = "$(MCS_LATEST_HASH_VERSION)"' $(VALUES_FILE)
	yq eval -i '(.$(MCS_TMLEAFNODE_CHART_NAME).midcbf.image.registry) = "$(MCS_DEV_IMAGE_REPO)"' $(VALUES_FILE)

	echo "Updating Chart.yaml to change $(EC_CHART_NAME) to $(EC_LATEST_HASH_VERSION) and repository to $(EC_DEV_HELM_REPO)"
	yq eval -i '(.dependencies[] | select(.name == "$(EC_CHART_NAME)").version) = "$(EC_LATEST_HASH_VERSION)"' $(CHART_FILE)
	yq eval -i '(.dependencies[] | select(.name == "$(EC_CHART_NAME)").repository) = "$(EC_DEV_HELM_REPO)"' $(CHART_FILE)

	echo "Updating values.yaml to change $(EC_CHART_NAME) to $(EC_LATEST_HASH_VERSION) and registry to $(EC_DEV_IMAGE_REPO)"
	yq eval -i '(.$(EC_CHART_NAME).engineeringconsole.image.tag) = "$(EC_LATEST_HASH_VERSION)"' $(VALUES_FILE)
	yq eval -i '(.$(EC_CHART_NAME).engineeringconsole.image.registry) = "$(EC_DEV_IMAGE_REPO)"' $(VALUES_FILE)

# k8s-pre-install-chart:
# 	@echo "k8s-pre-install-chart: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
# 	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)
# 	make update-chart MCS_HASH_VERSION=$(MCS_HASH_VERSION) EC_HASH_VERSION=$(EC_HASH_VERSION)

# k8s-pre-install-chart-car:
# 	@echo "k8s-pre-install-chart-car: creating the SDP namespace $(KUBE_NAMESPACE_SDP)"
# 	@make k8s-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP)

# k8s-pre-uninstall-chart:
# 	@echo "k8s-post-uninstall-chart: deleting the SDP namespace $(KUBE_NAMESPACE_SDP)"
# 	@if [ "$(KEEP_NAMESPACE)" != "true" ]; then make k8s-delete-namespace KUBE_NAMESPACE=$(KUBE_NAMESPACE_SDP); fi