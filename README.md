# pyar_infra
Python Argentina Infrastructure


## Redirecter.

We have lot of domains. But python.org.ar is our principal. 

To handle redirects from other domains we are using a nginx server. This server is handlign `redirecter.python.org.ar`
All domains except python.org.ar are pointing to it.

Nginx configuration is stored in a config-map: stable/pyar-rewrites/templates/config_map.yaml 

To deploy it run `helm upgrade --install pyar-rewrites --recreate-pods stable/pyar-rewrites`


## Pyarweb 

Python Argentina community website.

(WIP)
