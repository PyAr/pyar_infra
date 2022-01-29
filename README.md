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



### Staging


1. Get the static files from the docker image
```
$ docker run --name eventol -it eventol/eventol /bin/ash
$ docker ps
CONTAINER ID   IMAGE             COMMAND      CREATED          STATUS              PORTS      NAMES
2e88bd843642   eventol/eventol   "/bin/ash"   41 seconds ago   Up About a minute   8000/tcp   eventol
$ docker cp CONTAINER_ID:/usr/src/app/eventol/static .
```


2. Upload the static files to Azure Storage
```
az storage copy -s static -d 'https://pyareventol.file.core.windows.net/eventol-static/' --recursive
```

3. Deploy to [Staging:]

```bash
helm upgrade --install  --wait --timeout 60000 --values values/staging/eventol.yaml staging-eventos stable/eventol
```

### Produccion



1. Get the static files from the docker image (the version might change. Check the values/production/eventol.yaml file)
```
$ docker run --name eventol -it eventol/eventol:version-2.2.2 /bin/ash
$ docker ps
CONTAINER ID   IMAGE             COMMAND      CREATED          STATUS              PORTS      NAMES
2e88bd843642   eventol/eventol   "/bin/ash"   41 seconds ago   Up About a minute   8000/tcp   eventol
$ docker cp CONTAINER_ID:/usr/src/app/eventol/static .
```


2. Upload the static files to Azure Storage
```
az storage copy -s static -d 'https://pyareventol.file.core.windows.net/eventol-static/' --recursive
```

3. Deploy to [Production:](https://eventos.python.org.ar)
```bash
helm upgrade --install  --wait --timeout 60000 --values values/production/eventol.yaml production-eventos stable/eventol
```

## Asociación Civil administration. (asoc_members)

[Production](https://admin.ac.python.org.ar)


```bash
helm upgrade --install --wait --timeout 60000 --values values/production/asoc_members.yaml production-admin test/asoc-members
```


## PostgreSQL cluster:

Using https://github.com/helm/charts/tree/master/stable/postgresql

### Deploy:

```bash
helm install --name pgcluster -f values/production/postgres_cluster.yaml stable/postgresql
```


This cluster is using a PersistentVolumeClaim and a "lock" is created manually in azure to prevent unintensional deletes.
Detail about locks: https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-lock-resources

### Connect to the cluster

```bash
# get the password
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default pgcluster-postgresql -o jsonpath="{.data.postgresql-password}" | base64 --decode)
# connect
kubectl run pgcluster-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:11.4.0-debian-9-r34 --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- psql --host pgcluster-postgresql -U postgres -p 5432
```

###  Configuration

We have to create the databases and users manually


## Backups

(not documented)

## Wiki

Using https://github.com/helm/charts/tree/master/testing/wiki

### Deploy

```bash
helm upgrade --install --wait --timeout 60000 --values values/staging/pyar-wiki.yaml staging-wiki test/pyar-wiki --debug --recreate-pods
```

```bash
helm upgrade --install --wait --timeout 60000 --values values/production/pyar-wiki.yaml prod-wiki test/pyar-wiki --debug --recreate-pods
```

## Web

Using https://github.com/helm/charts/tree/master/testing/wiki

### Deploy

```bash
helm upgrade --install --wait --timeout 60000 --values values/staging/pyarweb.yaml pyarweb-staging test/pyarweb --debug --recreate-pods
```

```bash
helm upgrade --install --wait --timeout 60000 --values values/production/pyarweb.yaml pyarweb-production test/pyarweb --debug --recreate-pods
```

## Planeta 

```bash
helm upgrade --install --wait --timeout 60000 --values values/staging/planeta-pyar.yaml staging-planeta test/planeta-pyar --debug --recreate-pods
```

```bash
helm upgrade --install --wait --timeout 60000 --values values/production/planeta-pyar.yaml prod-planeta test/planeta-pyar --debug --recreate-pods
```