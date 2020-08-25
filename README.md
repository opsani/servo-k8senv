# servo-k8senv

Optune servo infrastructure plugin for Kubernetes (native)

When invoked, servo-k8senv:

* Parses JSON input from STDIN
* Gets the value or control.environment.mode, fail if not present (empty string OK)
* Get value of annotation current_mode_annotation (specified in the config) of k8s deployment deployment_name (specified in config). Missing annotation or empty value is an error
    1. If control.environment.mode == current_mode_annotation, exit 0 with status=ok 
    2. Otherwise, set the annotation desired_mode_annotation (from config) of k8s deployment deployment_name (specified in config) to the value of control.environment.mode. Failure to set the annotation will cause an error.

On successful update of the annotation, servo-k8senv will sleep for sleep_delay (value specified in config) seconds and return