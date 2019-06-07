# PyAr infrastructure 
Python Argentina Infrastructure
This is the repository with all the code and documentation to handle PyAr infrastructure


[![join our chat](https://img.shields.io/badge/zulip-join_chat-brightgreen.svg)](https://pyar.zulipchat.com/#streams/200416/Infra)

Our infrastructure have been hosted by [USLA](http://drupal.usla.org.ar/) for long time.

Currently we are migrating to [kubernetes](http://kubernetes.io/) in Azure [aks](https://docs.microsoft.com/en-us/azure/aks/)

We use [Helm](https://www.helm.sh/) as a package manager and [Keel](https://keel.sh/) for continuous delivery.

[Step-by-step guide to deploy de cluster](docs/k8s.md)

### HTTPS config

We are using HTTPS with [Let's Encrypt](https://letsencrypt.org/)

Settings details at: https://docs.microsoft.com/en-us/azure/aks/ingress

### Redirecter.

We have lot of domains. But python.org.ar is our principal. 

To handle redirects from other domains we are using a nginx server. This server is handlign `redirecter.python.org.ar`
All domains except python.org.ar are pointing to it.

Nginx configuration is stored in a config-map: stable/pyar-rewrites/templates/config_map.yaml 

To deploy it run: 

```bash 
helm upgrade --install --wait --recreate-pods pyar-rewrites stable/pyar-rewrites
```

## Python Argentina community website.
http://www.python.org.ar

Keel is upgrading the staging environment for each merge to `master`. 

A merge to master in [pyarweb](https://github.com/PyAr/pyarweb/) is triggering a new docker image build in [dockerhub](https://hub.docker.com/r/pyar/pyarweb/) and a web-hook is triggering Keel.

Production environment is still running in USLA. (manual deploy)

## Events site (EventoL)

https://eventos.python.org.ar 

Events site, using [EventoL](https://github.com/eventoL/eventoL). We use it to host PyDays, PyCon, Pycamp and other events.

[Production:](https://eventos.python.org.ar)

```bash
helm upgrade --install  --wait --timeout 60000 --values values/production/eventol.yaml production-eventos test/eventol
```

## Asociación Civil administration. (asoc_members)

[Production](https://admin.ac.python.org.ar)


```bash 
helm upgrade --install --wait --timeout 60000 --values values/production/asoc_members.yaml production-admin test/asoc-members
```
