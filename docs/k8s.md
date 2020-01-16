# Paso a paso para crear toda la infrastructura de PyAr desde cero. 

- requerimientos: 
    - clonar el repo de PyAr Infra: https://github.com/PyAr/pyar_infra
    - Permisos en la cuenta de azure de PyAr
    - kubectl 
    - helm (v2)
    - fades
    - az CLI (yo uso `az='fades -d azure-cli -x az'`)

## Crear el cluster de k8s

```bash 
az aks create -g pyar-infra -n flying-circus-v2 \
                --node-count 3 \
                --node-vm-size Standard_B2s \
                -k 1.13.5 \
                --dns-name-prefix flying-circus-v2 \
                -l eastus \
                --ssh-key-value .ssh/id_rsa_mail@gilgamezh.me.pub 
```

Esto va a deployar Kubernetes con 3 nodos en la versión 1.11.1. 
El tamaño de las VMs y la zona las seleccioné buscando la combinación más económica en [azureprice](https://azureprice.net/).

Una vez creado el cluster hay que configurar `kubectl` para que se conecte: 

```bash 
az aks get-credentials --resource-group pyar-infra --name flying-circus-v2
```

Testear ejecutando 

```
kubectl get nodes 
```

## Instalar Helm 

`helm init`

### Configurar permisos (RBAC) para Tiller (helm server side)


More at: https://helm.sh/docs/using_helm/#role-based-access-control

```bash 
# create service account
kubectl create serviceaccount tiller --namespace kube-system
# create ClusterRoleBinding 
kubectl create -f k8s/tiller-clusterrolebinding.yaml
# upgrade helm 
helm init --service-account tiller --upgrade
# test it 
helm ls
```

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


- crear namespace 
`kubectl create namespace ingress-basic`

- instalar nginx-ingress 

```bash 
helm install stable/nginx-ingress \
    --name production-nginx-ingress \
    --namespace ingress-basic \
    --set controller.replicaCount=2 \
    -f values/production/nginx-ingress.yaml\
```

- opcional, ejecutar este paso: https://docs.microsoft.com/en-us/azure/aks/ingress-tls#configure-a-dns-name


- instalar cert-manager 

```bash
# Install the CustomResourceDefinition resources separately
kubectl apply -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.8/deploy/manifests/00-crds.yaml

# Create the namespace for cert-manager
kubectl create namespace cert-manager

# Label the cert-manager namespace to disable resource validation
kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true

# Add the Jetstack Helm repository
helm repo add jetstack https://charts.jetstack.io

# Update your local Helm chart repository cache
helm repo update

# Install the cert-manager Helm chart
helm install \
  --name cert-manager \
  --namespace cert-manager \
  --version v0.8.0 \
  jetstack/cert-manager
```

- Cear CA cluster issuer 

```bash 
kubectl create -f k8s/letsencrypt/cluster-issuer.yaml
```

## Install keel for continuos delivery

clone keel master as the chart is updated to us ingress. then

`helm upgrade --install keel path/to/chart/keel --values values/production/keel.yaml --namespace=kube-system`

## Hints:

- Una vez que k8s esta funcionando se puede continuar con los pasos detallados en README.md para cada proyecto. 
- Estamos usando PSQL en una VM con ubuntu administrado "manualmente" porque el postgres de azure es **MUUUY LENTO** 
- Para los sitios que usan SSL no hace falta IP publica. siempre usar la del ingress. 
- https://kubernetes.io/docs/reference/kubectl/cheatsheet/ 
