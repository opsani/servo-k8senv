import io
import json
import kubernetes
from kubernetes.client.models import V1Container, V1ContainerPort, V1Deployment, V1DeploymentSpec, V1LabelSelector, V1Namespace, V1ObjectMeta, V1PodSpec, V1PodTemplateSpec, V1ResourceRequirements
import os
import pytest
import sys

os.environ['OPTUNE_CONFIG'] = 'test_config.yaml'
from environment import run

adjust_stdin_json_obj = {
    "control" : { "environment": { "mode": "canary" } },
    "application": {
        "components": {
            "co-http": {
                "settings": {
                    "cpu": {"value": 0.25},
                    "mem": {"value": 0.5},
                    "replicas": {"value": 1},
                    "GOGC": {"value": 90},
                    "TEST": {"value": "B"}
                }
            }
        }
    }
}

test_dep = V1Deployment(
    'apps/v1', 
    'Deployment', 
    V1ObjectMeta(name='web-main', labels={'app': 'web'}, annotations={'opsani-current-mode': 'canary'}), 
    V1DeploymentSpec(
        replicas=3,
        selector=V1LabelSelector(match_labels={'app': 'web', 'role': 'main'}),
        template=V1PodTemplateSpec(
            metadata=V1ObjectMeta(labels={'app': 'web', 'role': 'main'}),
            spec=V1PodSpec(containers=[V1Container(
                name='main',
                image='opsani/co-http:latest',
                args=['busy=400'],
                resources=V1ResourceRequirements(
                    limits={'cpu': '125m', 'memory': '512Mi'},
                    requests={'cpu': '125m', 'memory': '512Mi'}
                ),
                ports=[V1ContainerPort(container_port=8080)]
            )])
        )
    )
)

def setup_module(module):
    if os.getenv('KUBERNETES_SERVICE_HOST'): # If running in a kubernetes cluster
        kubernetes.config.load_incluster_config()
    else:
        kubernetes.config.load_kube_config()

    # setup desired ns
    kubernetes.client.CoreV1Api().create_namespace(body=V1Namespace(api_version='v1', kind='Namespace', metadata=V1ObjectMeta(name='opsani')))

    pytest.apps_client = kubernetes.client.AppsV1Api()
    _ = pytest.apps_client.create_namespaced_deployment(namespace='opsani', body=test_dep)
    test_dep.metadata.name = 'web-canary'
    _ = pytest.apps_client.create_namespaced_deployment(namespace='default', body=test_dep)

def test_environment_ok(monkeypatch, capsys):
    with monkeypatch.context() as m:
        m.setattr(sys, 'stdin', io.StringIO(json.dumps(adjust_stdin_json_obj)))
        run()
        assert json.loads(capsys.readouterr().out)['status'] == 'ok'

def test_environment_mismatch(monkeypatch, capsys):
    adjust_stdin_json_obj["control"]["environment"]["mode"] = "mainline"
    with monkeypatch.context() as m:
        m.setattr(sys, 'stdin', io.StringIO(json.dumps(adjust_stdin_json_obj)))
        run()

        updated_dep = pytest.apps_client.read_namespaced_deployment('web-main', 'opsani')
        assert updated_dep.metadata.annotations.get('opsani-desired-mode') == "mainline", \
            'Desired mode annotation not found in updated deployment metadata. Dep: {}'.format(updated_dep)
        assert json.loads(capsys.readouterr().out)['status'] == 'environment-mismatch'

def teardown_module(module):
    pytest.apps_client.delete_namespaced_deployment(name='web-canary', namespace='default')
    pytest.apps_client.delete_namespaced_deployment(name='web-main', namespace='opsani')
    kubernetes.client.CoreV1Api().delete_namespace(name='opsani')
