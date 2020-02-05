#!/usr/bin/env fades


# This script is to remove metadata annotations from a k8s secret file
# obtained using `kubectl get secret <secret-name> -o yaml`
# it will read from stdin and print the yaml file deleting the keys listed
# in KEYS_TO_REMOVE

import sys

import yaml  # fades


METADATA_K_TO_REMOVE = ["creationTimestamp", "resourceVersion"]
ANN_K_TO_REMOVE = ["kubectl.kubernetes.io/last-applied-configuration"]



secret_yaml = yaml.load(sys.stdin.read(), Loader=yaml.FullLoader)
if 'metadata' in secret_yaml.keys():
    new_metadata = {
        k: v for k, v in secret_yaml['metadata'].items() if k not in METADATA_K_TO_REMOVE}
    if "annotations" in new_metadata:
        new_annotations = {
            k: v for k, v in new_metadata['annotations'].items() if k not in ANN_K_TO_REMOVE}
        new_metadata['annotations'] = new_annotations
    secret_yaml['metadata'] = new_metadata

print(yaml.dump(secret_yaml))
