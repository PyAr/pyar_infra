#!/bin/bash

alias az='fades -p python3.6 -d azure-cli -x az'
# Public IP address of your ingress controller
IP="52.168.19.255"  # WARNING!!! UPDATE WITH THE CLUSTER IP

# Name to associate with public IP address
DNSNAME="redirecter.python.org.ar"

# Get the resource-id of the public ip
PUBLICIPID=$(az network public-ip list --query "[?ipAddress!=null]|[?contains(ipAddress, '$IP')].[id]" --output tsv)

# Update public ip address with DNS name
az network public-ip update --ids $PUBLICIPID --dns-name $DNSNAME
