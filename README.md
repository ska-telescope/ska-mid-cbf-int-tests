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
    * [Data Access Through importlib.resources](#data-access-through-importlibresources)
    * [Client Interfaces](#client-interfaces)
    * [Sphinx API Auto-Documentation](#sphinx-api-auto-documentation)


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
    <li> Fill in the parameters in notebook_parameters.json, importantly "kube_namespace" will need to be set as the name of the created namespace
    <li> Begin running an ipython kernel with command "jupyter-notebook --no-browser"
    <li> Open the notebooks in notebooks/prototyping
    <li> Run the notebooks going in index order and following listed instructions in notebook if any
</ol>

Cleaning up the notebook to upload to Gitlab: in the local code repo run scripts/clear-notebooks-data.sh to clear outputs and metadata on all notebooks in the notebooks directory

# Technical Notes

## Data Access Through importlib.resources

## Client Interfaces

## Sphinx API Auto-Documentation

