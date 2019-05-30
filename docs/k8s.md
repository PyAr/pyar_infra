# Paso a paso para crear toda la infrastructura de PyAr desde cero. 

- requerimientos: 
    - clonar el repo de PyAr Infra: https://github.com/PyAr/pyar_infra
    - Permisos en la cuenta de azure de PyAr
    - kubectl 
    - helm 
    - az CLI (yo uso `az='fades -d azure-cli -x az'`)

## Crear el cluster de k8s

```bash 
az aks create -g pyar-infra -n flying-circus \
                --node-count 3 \
                --node-vm-size Standard_B2s \
                -k 1.11.1 --disable-rbac \
                --dns-name-prefix flying-circus \
                -l eastus \
                --ssh-key-value .ssh/id_rsa_mail@gilgamezh.me.pub 
```

Esto va a deployar Kubernetes con 3 nodos en la versión 1.11.1. 
El tamaño de las VMs y la zona las seleccioné buscando la combinación más económica en [azureprice](https://azureprice.net/).

Una vez creado el cluster hay que configurar `kubectl` para que se conecte: 

```bash 
az aks get-credentials --resource-group pyar-infra --name flying-circus
```

Testear ejecutando 

```
kubectl get nodes 
```

## Instalar Helm 

`helm init`

## crear secretos 

>  (:warning: no están en el repo)

```bash 
kubectl apply -f /path/to/secrets/files/
```

### Actualizar secretos: 


Con el script `dump_k8s_secrets.sh` es posible hacer un dump de los secretos del cluster. 
Se recomienda guardarlos en un repo .git y utilizar este script como si fuese un "PULL" y apply como 
si fuese un "PUSH"

```bash 
scripts/dump_k8s_secrets.sh /path/to/secrets/files/
## modificar los secretos 
kubectl apply -f /path/to/secrets/files/
```

## Configurar nginx-ingress con Let's Encrypt. 

Detalles en: https://docs.microsoft.com/en-us/azure/aks/ingress

- instalar nginx-ingress 

```bash 
helm install stable/nginx-ingress --namespace kube-system\
                                  --set rbac.create=false\
                                  -f values/production/nginx-ingress.yaml\
                                  --name production-nginx-ingress
```

- instalar cert-manager 

```bash
helm install --name prod-cert-manager stable/cert-manager \
             --set ingressShim.defaultIssuerName=letsencrypt-prod \
             --set ingressShim.defaultIssuerKind=ClusterIssuer \
             --set rbac.create=false \
             --set serviceAccount.create=false
```

- Cear CA cluster issuer 

```bash 
kubectl create -f letsencrypt/cluster-issuer.yaml
```

- Crear certificados 

```bash 
kubectl create -f letsencrypt/certificates.yaml
```


## Hints:

- Una vez que k8s esta funcionando se puede continuar con los pasos detallados en README.md para cada proyecto. 
- Estamos usando PSQL en una VM con ubuntu administrado "manualmente" porque el postgres de azure es **MUUUY LENTO** 
- Para los sitios que usan SSL no hace falta IP publica. siempre usar la del ingress. 
- https://kubernetes.io/docs/reference/kubectl/cheatsheet/ 
