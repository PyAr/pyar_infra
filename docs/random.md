# Cosas Random


## Como Borrar Viejos Backups


1. Primero necesitamos la key del account. Para eso hay que correr este comando

```
$  az storage account keys list --resource-group MC_pyar-infra_flying-circus-v3_eastus --account-name pyarbackups
```

2. Borrar los archivos con la key que obtenemos de ese comando
```
$ az storage file delete-batch --account-key EL_VALOR_DEL_COMANDO_ANTERIOR_SIN_CAMBIAR_NADA --account-name pyarbackups --pattern 'backupOn2023-07*' -s pvc-458c5ae7-d0b7-4038-b6c2-205aff6e71a5
```