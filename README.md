# Python Argentina Infrastructure

This is the repository with all the code and documentation to handle PyAr infrastructure

We are working with [kubernetes](http://kubernetes.io/) in Azure [aks](https://docs.microsoft.com/en-us/azure/aks/)

We use [Helm](https://www.helm.sh/) as a package manager.

[Step-by-step guide to deploy de cluster](docs/k8s.md)


## HTTPS config

We are using HTTPS with [Let's Encrypt](https://letsencrypt.org/)

Settings details at: https://docs.microsoft.com/en-us/azure/aks/ingress


## Redirecter.

We have lot of domains. But python.org.ar is our principal.

To handle redirects from other domains we have two models:

1. nginx ingress rules, different services configured with files in the `redirects` directory

    - first time:
    
        kubectl create -f redirects/prueba.yaml

    - after any change:

        kubectl apply -f redirects/prueba.yaml

    - to see what's there:

        kubectl get pods --namespace=ingress-basic

2. nginx server, handling `redirecter.python.org.ar`, the configuration is stored in a config-map: `stable/pyar-rewrites/templates/config_map.yaml`, to deploy it run:

```bash
helm upgrade --install --wait pyar-rewrites stable/pyar-rewrites
```


## The Database, a PostgreSQL cluster

Using https://github.com/helm/charts/tree/master/stable/postgresql


### Deploy:

El siguiente comando hace el deploy. NOTA: NO tiene que estar el secreto `pgcluster-postgresql` al momento de deployar PSQL (se crea en ese proceso).

```bash
helm upgrade --install --wait -f values/production/postgres_cluster.yaml pgcluster oci://registry-1.docker.io/bitnamicharts/postgresql
```

This cluster is using a PersistentVolumeClaim and a "lock" is created manually in azure to prevent unintencional deletes. Detail about locks: https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-lock-resources

To set the backup:

```bash
kubectl apply -f k8s/pgsql_bkps_jobs/pg-storage-class.yaml
kubectl apply -f k8s/pgsql_bkps_jobs/pg-persistent-volume-claim.yaml
kubectl apply -f k8s/pgsql_bkps_jobs/pg-backup-cronJob.yaml
```



### Connect to the cluster

```bash
# get the password
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default pgcluster-postgresql -o jsonpath="{.data.postgres-password}" | base64 --decode)
# connect
kubectl run pgcluster-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:11.5.0-debian-9-r84 --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- psql --host pgcluster-postgresql -U postgres -p 5432
```


###  Configuration

We have to create the databases and users manually


### Restore backups

1. Download the Backup file from Azure Blob Storage
1. Create a console to the PostgreSQL cluster
```bash
# get the password
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default pgcluster-postgresql -o jsonpath="{.data.postgres-password}" | base64 --decode)
# connect
kubectl run pgcluster-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:11.5.0-debian-9-r84 --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- /bin/bash
```

1. On a new local console, copy the local downloaded file to the cluster
```bash
kubectl cp *.dump pgcluster-postgresql-client:/tmp/backup
```

1. On the existing console to the PostgreSQL cluster run the restore command. Change the `CHANGE_THE_DATABASE` for the correct value
```bash
I have no name!@pgcluster-postgresql-client:/$ pg_restore --host pgcluster-postgresql -U postgres --d CHANGE_THE_DATABASE /tmp/backup
```

## Python Argentina community website

http://www.python.org.ar

```bash
helm upgrade --install --wait --timeout 120s --values values/production/pyarweb.yaml pyarweb-production stable/pyarweb
```


## Wiki

Using https://github.com/helm/charts/tree/master/testing/wiki

Staging:

```bash
helm upgrade --install --wait --timeout 120s --values values/staging/pyar-wiki.yaml staging-wiki stable/pyar-wiki --debug
```

Production:

```bash
helm upgrade --install --wait --timeout 120s --values values/production/pyar-wiki.yaml prod-wiki stable/pyar-wiki --debug
```


## Asociación Civil administration. (asoc_members)

[Production](https://admin.ac.python.org.ar)


```bash
helm upgrade --install --wait --timeout 120s --values values/production/asoc_members.yaml production-admin stable/asoc-members
```

## Join Captcha bot

```bash
helm upgrade --install  --wait --timeout 120s --values values/production/join_captcha_bot.yaml captcha-bot-production stable/join_captcha_bot
```

Once up, talk through Telegram with the bot itself and issue: `/allowgroup add CHAT_ID` (the CHAT_ID can be seen in the logs doing something similar to `kubectl logs captcha-bot-production-5d99c5595d-8wcbb`).


## Events site (EventoL)

https://eventos.python.org.ar

Events site, using [EventoL](https://github.com/eventoL/eventoL). We use it to host PyDays, PyCon, Pycamp and other events.


### Staging

1. Get the static files from the docker image (the version might change. Check the values/staging/eventol.yaml file)
```
$ docker run --name eventol -it registry.gitlab.com/eventol/eventol/releases:v2.3.2 /bin/ash
$ docker ps
CONTAINER ID   IMAGE             COMMAND      CREATED          STATUS              PORTS      NAMES
2e88bd843642   eventol/eventol   "/bin/ash"   41 seconds ago   Up About a minute   8000/tcp   eventol
$ docker cp CONTAINER_ID:/usr/src/app/eventol/static .
```


2. Upload the static files to Azure Storage
```
cd static
az storage copy -s static -d 'https://pyareventol.file.core.windows.net/eventol-static/' --recursive
```

3. Deploy to [Staging:]

```bash
helm upgrade --install  --wait --timeout 60000 --values values/staging/eventol.yaml staging-eventos stable/eventol
```

### Production


1. Get the static files from the docker image (the version might change. Check the values/production/eventol.yaml file)
```
$ docker run --name eventol -it registry.gitlab.com/eventol/eventol/releases:v2.3.2 /bin/ash
$ docker ps
CONTAINER ID   IMAGE             COMMAND      CREATED          STATUS              PORTS      NAMES
2e88bd843642   eventol/eventol   "/bin/ash"   41 seconds ago   Up About a minute   8000/tcp   eventol
$ docker cp CONTAINER_ID:/usr/src/app/eventol/static .
```


2. Upload the static files to Azure Storage
```|
cd static
az storage copy -s static -d 'https://pyareventol.file.core.windows.net/eventol-prod-static/' --recursive
```

3. Deploy to [Production:](https://eventos.python.org.ar)
```bash
helm upgrade --install  --wait --timeout 120s --values values/production/eventol.yaml production-eventos stable/eventol
```
