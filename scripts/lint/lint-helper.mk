# Quickly fix isort lint issues
python-fix-isort:
	$(PYTHON_RUNNER) isort --profile black --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(PYTHON_LINT_TARGET)

# Quickly fix black line issues
python-fix-black:
	$(PYTHON_RUNNER) black --exclude .+\.ipynb --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(PYTHON_LINT_TARGET)

# Quickly fix notebook isort lint issues
notebook-fix-isort:
	$(PYTHON_RUNNER) nbqa isort --profile=black --line-length=$(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(NOTEBOOK_SWITCHES_FOR_ISORT) $(NOTEBOOK_LINT_TARGET)

# Quickly fix notebook black line issues
notebook-fix-black:
	$(PYTHON_RUNNER) nbqa black --line-length=$(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(NOTEBOOK_SWITCHES_FOR_BLACK) $(NOTEBOOK_LINT_TARGET)