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
az aks create -g pyar-infra -n flying-circus-v3 \
                --node-count 4 \
                --node-vm-size Standard_B2s \
                -k 1.26.3 \
                --dns-name-prefix flying-circus-v2 \
                -l eastus \
                --ssh-key-value .ssh/id_rsa_mail@gilgamezh.me.pub 
```

Esto va a deployar Kubernetes con 4 nodos en la versión 1.26.3. 
El tamaño de las VMs y la zona las seleccioné buscando la combinación más económica en [azureprice](https://azureprice.net/).

Una vez creado el cluster hay que configurar `kubectl` para que se conecte: 

```bash 
az aks get-credentials --resource-group pyar-infra --name flying-circus-v3
```

Testear ejecutando 

```
kubectl get nodes 
```

## Instalar Helm 

Local en tu máquina, instrucciones:

   https://helm.sh/docs/intro/install/ 

## Crear secretos 

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

- crear un controlador ingress

```bash
NAMESPACE=ingress-basic

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace $NAMESPACE \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
```

- ver cómo quedó: `kubectl --namespace ingress-basic get services -o wide -w ingress-nginx-controller`

    NOTA: la IP pública que muestra acá es la que tenemos que apuntar desde Cloudflare en la entrada `k8s_ingress` en `python.org.ar`

- crear un container registry (ACR)

```bash
REGISTRY_NAME=pyaracr
az acr create -n $REGISTRY_NAME -g pyar-infra --sku basic
az aks update -n flying-circus-v3 -g pyar-infra --attach-acr $REGISTRY_NAME
```

- para habilitar TLS con Let's Encrypt:

```bash
CERT_MANAGER_REGISTRY=quay.io
CERT_MANAGER_TAG=v1.8.0
CERT_MANAGER_IMAGE_CONTROLLER=jetstack/cert-manager-controller
CERT_MANAGER_IMAGE_WEBHOOK=jetstack/cert-manager-webhook
CERT_MANAGER_IMAGE_CAINJECTOR=jetstack/cert-manager-cainjector

az acr import --name $REGISTRY_NAME --source $CERT_MANAGER_REGISTRY/$CERT_MANAGER_IMAGE_CONTROLLER:$CERT_MANAGER_TAG --image $CERT_MANAGER_IMAGE_CONTROLLER:$CERT_MANAGER_TAG
az acr import --name $REGISTRY_NAME --source $CERT_MANAGER_REGISTRY/$CERT_MANAGER_IMAGE_WEBHOOK:$CERT_MANAGER_TAG --image $CERT_MANAGER_IMAGE_WEBHOOK:$CERT_MANAGER_TAG
az acr import --name $REGISTRY_NAME --source $CERT_MANAGER_REGISTRY/$CERT_MANAGER_IMAGE_CAINJECTOR:$CERT_MANAGER_TAG --image $CERT_MANAGER_IMAGE_CAINJECTOR:$CERT_MANAGER_TAG

ACR_URL=pyaracr.azurecr.io

kubectl label namespace ingress-basic cert-manager.io/disable-validation=true
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install the cert-manager Helm chart
helm install cert-manager jetstack/cert-manager \
  --namespace ingress-basic \
  --version=$CERT_MANAGER_TAG \
  --set installCRDs=true \
  --set nodeSelector."kubernetes\.io/os"=linux \
  --set image.repository=$ACR_URL/$CERT_MANAGER_IMAGE_CONTROLLER \
  --set image.tag=$CERT_MANAGER_TAG \
  --set webhook.image.repository=$ACR_URL/$CERT_MANAGER_IMAGE_WEBHOOK \
  --set webhook.image.tag=$CERT_MANAGER_TAG \
  --set cainjector.image.repository=$ACR_URL/$CERT_MANAGER_IMAGE_CAINJECTOR \
  --set cainjector.image.tag=$CERT_MANAGER_TAG
```

- Cear CA cluster issuer 

```bash 
kubectl apply -f k8s/letsencrypt/cluster-issuer.yaml --namespace ingress-basic
```

## Hints:

- Una vez que k8s esta funcionando se puede continuar con los pasos detallados en README.md para cada proyecto. 
- Estamos usando PSQL en una instancia de k8s porque el postgres de azure es **MUUUY LENTO** 
- Para los sitios que usan SSL no hace falta IP publica. siempre usar la del ingress. 
- https://kubernetes.io/docs/reference/kubectl/cheatsheet/ 
