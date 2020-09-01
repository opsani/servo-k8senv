# servo-k8senv

Optune servo infrastructure plugin for Kubernetes (native)

When invoked, servo-k8senv:

* Parses JSON input from STDIN
* Gets the value or control.environment.mode, fail if not present (empty string OK)
* Get value of annotation current_mode_annotation (specified in the config) of k8s deployment deployment_name (specified in config). Missing annotation or empty value is an error
    1. If control.environment.mode == current_mode_annotation, exit 0 with status=ok 
    2. Otherwise, set the annotation desired_mode_annotation (from config) of k8s deployment deployment_name (specified in config) to the value of control.environment.mode. Failure to set the annotation will cause an error.

On successful update of the annotation, servo-k8senv will sleep for sleep_delay (value specified in config) seconds and return

## Configuration Format

```yaml
k8senv:
  deployment_name: AAA # required
  namespace: default # optional
  current_mode_annotation: BBB # required
  desired_mode_annotation: CCC # required
  sleep_delay: 120 # optional
```

## Running the tests

The tests are meant to be run by `pytest`. The Python3 version is required, it can be installed with
the OS package manager (see example setup below) or with `python3 -m pip install pytest`.

To run the tests, get a copy of the opsani/servo-k8senv repo on a host that has `minikube` installed
and running (`minikube start`). There should be no deployments in the default namespace (verify this by running
`kubectl get deployment`).

Example setup:

```bash
# this setup assumes Ubuntu 18.4, for earlier versions, please install pip and pytest for Python3 manually, start from
# `https://pip.pypa.io/en/stable/installing/` for setting up pip.
sudo apt-get install -y python3-pytest

git clone git clone git@github.com:opsani/servo-k8senv
cd ~/servo-k8senv/test
ln -s ../environment ./environment.py # symlink and rename to allow test suite to import as module

# run the tests
python3 -m pytest
```
