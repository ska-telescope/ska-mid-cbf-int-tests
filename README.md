# SKA Mid.CBF I&T Tests

This repository contains testing and prototyping Python code for CIPA team integration testing of internal CBF components, largely driven by issuing commands to MCS.

Code repository: [here](https://gitlab.com/ska-telescope/ska-mid-cbf-int-tests)

ReadtheDocs: [here](https://developer.skao.int/projects/ska-mid-cbf-int-tests/en/latest/)

# Table Of Contents
* [Guides](#guides)
    * [Setup I&T Tests](#setup-it-tests)
    * [Using Namespaces](#using-namespaces)
    * [Automated Testing](#automated-testing)
    * [Prototyping Notebook](#prototyping-notebook)
* [Technical Notes](#technical-notes)
    * [LMC Emulation for MCS Interaction](#lmc-emulation-for-mcs-interaction)
    * [Data Access Through importlib.resources](#data-access-through-importlibresources)
    * [Docstring Style and Sphinx API Auto-Documentation](#docstring-style-and-sphinx-api-auto-documentation)


# Guides

## Setup I&T Tests

<ol>
    <li> Clone the repository: git clone https://gitlab.com/ska-telescope/ska-mid-cbf-int-tests.git
    <li> Create a virtual environment: python3.10 -m venv *path-ending-in-dir-of-venv-name*
    <li> Activate the virtual environment: source *path-ending-in-dir-of-venv-name*/bin/activate
    <li> Install poetry: pip install poetry
    <li> Navigate into the cloned repository
    <li> Install dependencies to the venv: poetry install
</ol>

## Using Namespaces

Creating a namespace:

<ol>
    <li> Open the Gitlab repository in a browser
    <li> Navigate to Pipelines
    <li> Click New pipeline, and identify the newly created pipeline associated with your username
    <li> Wait for initial jobs to run
    <li> Select the on_demand stage and the mid-on-demand-deploy job
    <li> Click run on the job, once completed this will create a namespace for you, the name of the namespace created will be viewable in the job log
</ol>

Redeploying a namespace: run the mid-on-demand-redeploy job

Destroying a namespace: either run the mid-on-demand-destroy job in stage cleanup or if not available run command "kubectl delete namespace \*name-of-namespace\*" on a node connected to the relevant cluster. Destruction will be automatically run if automated testing is run on Gitlab.

## Automated Testing

Required parameters:
- PYTEST_MARKER: test set to run valid values can be found in pytest.ini

Running automated testing:
<ol>
<li> Run the steps to create a namespace
   <li> For running on Gitlab:
   <ol>
        <li> Click into the python-test job in the test stage 
        <li> Fill the variables in with the above listed required parameters
        <li> Run the job
   </ol>
   <li> For running locally:
   <ol>
        <li> Ensure you're running on a machine that can access the relevant kubernetes cluster of the created namespace
        <li> Navigate to your local code repository
        <li> Run command "make python-test KUBE_NAMESPACE=*namespace-name* KEYWORD1=VALUE1 KEYWORD2=VALUE2 ..." replacing *namespace-name* with the name of the created namespace and KEYWORDn, VALUEn pairs with the above required parameters
   </ol>
</ol>

## Prototyping Notebook

Running the notebook:

<ol>
    <li> Run the steps to create a namespace
    <li> Ensure you're running on a machine that can access the relevant kubernetes cluster of the created namespace
    <li> Navigate to the notebooks/prototyping directory in the local code repository 
    <li> Fill in the parameters in notebook_parameters.json, explanation of the parameters is located in the accompanying notebook_params_README.md
    <li> Begin running an ipython kernel with command "jupyter-notebook --no-browser"
    <li> Open the notebooks in notebooks/prototyping
    <li> Run the notebooks going in index order and following listed instructions in notebook if any
</ol>

Cleaning up the notebook to upload to Gitlab: in the local code repo run scripts/clear-notebooks-data.sh to clear outputs and metadata on all notebooks in the notebooks directory

# Technical Notes

## LMC Emulation for MCS Interaction

Code in ska_mid_cbf_int_tests philosophically should seek to mirror the emulation of LMC as much as possible through its interactions with MCS. See this as a kind of guiding light for this repository. See [https://developer.skao.int/projects/ska-mid-cbf-mcs/en/latest/guide/interfaces/lmc_mcs_interface.html](https://developer.skao.int/projects/ska-mid-cbf-mcs/en/latest/guide/interfaces/lmc_mcs_interface.html) for the expected interface. This is important to do as replicating LMC behavior increases the accuracy of tests and prototyping to its final product usage and accordingly increases the probability that the finished Mid.CBF product will be successful in the actual telescope. This further reduces integration issues down the line, especially ensuring that site acceptance and other teams' integration work is successful. An example of doing this is the SubarrayClient in ska_mid_cbf_int_tests in cbf_command which replicates commands in the LMC-MCS interface directly and only additionally contains subroutines that would be possible sequences for LMC to run. 

## Data Access Through importlib.resources

The paradigm for data access in ska_mid_cbf_int_tests is to use the modern Python library of importlib.resources (python >=3.7) to import data through Python's import builtin system. This allows data to be imported anywhere in the repository as long as the project is built and installed (via poetry) and corresponding data is included in that build. This is necessary such that data can be commonly used in both the testing executions and also the notebooks executions without tying to specific common relative paths which would introduce high coupling to the data location. See [https://docs.python.org/3/library/importlib.resources.html](https://python-poetry.org/docs/pyproject/#exclude-and-include) for further information and usage.

This means data must be kept in the build directories (src directory) and included in the installed package of the repository which is also under the name ska_mid_cbf_int_tests. Data must be registered in the build specification to be included in the ska_mid_cbf_int_tests package build, as only .py files are included default. Modify the pyproject.toml "include" variable to include non py files as per [https://python-poetry.org/docs/pyproject/#exclude-and-include](https://python-poetry.org/docs/pyproject/#exclude-and-include).

## Docstring Style and Sphinx API Auto-Documentation

The docstring style of ska_mid_cbf_int_tests is sphinx [https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html). This is necessary for automatic API documentation using the sphinx autodoc extension.

Reference [https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) to see how to setup autodoc, such that it automatically generates API documentation from API docstrings in the generated ReadtheDocs pages. Modify files in docs as appropriate to implement this. Importantly, two things to be aware of:
- Documentation for modules may just generate nothing which commonly is caused by the module not being importable to docs generation code. This requires modifying sys.path attributes in conf.py in the docs directory to get the module importable and recognized.
- API to be documented requires all of their dependencies installed since they are imported as normal modules for documentation generation, so ensure that the docs dependencies group includes all normal dependencies of the API.