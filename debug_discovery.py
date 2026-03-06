import urllib3
import logging

try:
    from kubernetes import client as k8s_client, config as k8s_config
except ImportError:
    pass
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("kubernetes.client.rest").setLevel(logging.ERROR)

k8s_config.load_kube_config()
k8s_v1 = k8s_client.CoreV1Api()

def get_pod_warnings(namespace: str, pod_name: str) -> list:
    if not k8s_v1: return []
    warnings = []
    try:
        fs = f"involvedObject.name={pod_name},type=Warning"
        events = k8s_v1.list_namespaced_event(namespace, field_selector=fs).items
        events.sort(key=lambda x: x.last_timestamp or x.event_time or datetime.min, reverse=True)
        for e in events[:5]:
            warnings.append({"reason": e.reason, "message": e.message, "count": e.count, "time": e.last_timestamp.isoformat() if e.last_timestamp else None})
    except Exception as e:
        print(f"Warning fetch error: {e}")
    return warnings

import traceback
try:
    res = k8s_v1.list_pod_for_all_namespaces()
    pods = []
    found_pods = set()
    for pod in res.items:
        pname = pod.metadata.name.lower()
        labels = pod.metadata.labels or {}
        is_mongot = (
            labels.get("app.kubernetes.io/component") == "search" or 
            labels.get("app") == "mongodbsearch" or
            ("mongot" in pname and "mongod" not in pname) or
            ("search" in pname and "operator" not in pname)
        )
        if not is_mongot or pod.metadata.name in found_pods: continue
        found_pods.add(pod.metadata.name)
        
        containers = []
        cpu_limit_cores = 0.0

        for c in (pod.spec.containers or []):
            if c.resources and c.resources.limits and "cpu" in c.resources.limits:
                cpu_str = c.resources.limits["cpu"]
                try:
                    if cpu_str.endswith("m"): cpu_limit_cores += int(cpu_str[:-1]) / 1000.0
                    else: cpu_limit_cores += float(cpu_str)
                except: pass

        for cs in (pod.status.container_statuses or []):
            last_reason = None
            if cs.last_state and cs.last_state.terminated: last_reason = cs.last_state.terminated.reason
            containers.append({
                "name": cs.name, "ready": cs.ready, "restart_count": cs.restart_count,
                "state": "running" if cs.state.running else "waiting" if cs.state.waiting else "terminated" if cs.state.terminated else "unknown",
                "last_reason": last_reason
            })

        print(f"Matched pod: {pname}")
        pods.append({
            "name": pod.metadata.name, "namespace": pod.metadata.namespace,
            "node": pod.spec.node_name, "pod_ip": pod.status.pod_ip,
            "phase": pod.status.phase,
            "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None,
            "containers": containers,
            "total_restarts": sum(c["restart_count"] for c in containers),
            "all_ready": all(c["ready"] for c in containers) if containers else False,
            "cpu_limit_cores": cpu_limit_cores,
            "warnings": get_pod_warnings(pod.metadata.namespace, pod.metadata.name)
        })
    print(f"Total pods matched: {len(pods)}")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()

