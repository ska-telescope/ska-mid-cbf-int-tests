PROJECT = ska-mid-cbf-int-tests

# include core make support
include .make/base.mk

# include raw support
include .make/raw.mk

# include OCI Images support
include .make/oci.mk

# include k8s support
include .make/k8s.mk

# Include Python support
include .make/python.mk

PYTEST_MARKER ?=
ALO_ASSERTING ?= 1

KUBE_NAMESPACE = ci-ska-mid-cbf-system-tests-1713695081-bremedios
TANGO_HOST ?=  databaseds-tango-base:10000
# 192.168.128.236:10000
CLUSTER_DOMAIN = cluster.local

# Add verbosity and INFO logging to python-test
PYTHON_VARS_AFTER_PYTEST = -v --capture=no --log-cli-level=INFO --alo-asserting $(ALO_ASSERTING) --namespace $(KUBE_NAMESPACE) --cluster-domain $(CLUSTER_DOMAIN) --tango-host $(TANGO_HOST)

# justification: redefined-outer-name must be disabled for pytest fixtures
# justification: unused-argument must be disabled for pytest fixtures
PYTHON_SWITCHES_FOR_PYLINT = --disable=redefined-outer-name,unused-argument

# Quickly fix isort lint issues
python-fix-isort:
	$(PYTHON_RUNNER) isort --profile black --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(PYTHON_LINT_TARGET)

# Quickly fix black line issues
python-fix-black:
	$(PYTHON_RUNNER) black --exclude .+\.ipynb --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(PYTHON_LINT_TARGET)