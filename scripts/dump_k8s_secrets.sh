#!/bin/bash 

set -e

OUTPUT_PATH=$1
SCRIPT_PATH=$(dirname $0)
echo -e "\n\n This script is going to dump all k8s secrets to yaml files in $OUTPUT_PATH \n\n"

if [[ $# -eq 0 ]] ; then
    echo 'indicate the output path as an argument. IE: "./dump_k8s_secrets.sh /tmp/output_path/"'
    exit 1
fi
# create the output path if it doesn't exists.
mkdir -p $OUTPUT_PATH
# export variables to be avilable in child process
export OUTPUT_PATH
export SCRIPT_PATH
kubectl get --no-headers secrets | awk '{print $1}' | xargs -I{} sh -c 'kubectl get secret -o yaml "$1" | $SCRIPT_PATH/remove_metadata.py > "$OUTPUT_PATH/$1.yaml"' - {} 
