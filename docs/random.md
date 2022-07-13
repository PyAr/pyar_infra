# Cosas Random


## Como Borrar Viejos Backups


1. Primero necesitamos la key del account. Para eso hay que correr este comando

```
$  az storage account keys list --resource-group MC_pyar-infra_flying-circus-v2_eastus --account-name pyarbackups
```

2. Borrar los archivos con la key que obtenemos de ese comando
```
$ az storage file delete-batch --account-key EL_VALOR_DEL_COMANDO_ANTERIOR_SIN_CAMBIAR_NADA --account-name pyarbackups --pattern 'backupOn2022-02*' -s kubernetes-dynamic-pvc-5968ddc2-d7ed-11e9-89ad-2636291a1cb5
```