readme doesn't instruct for protobuf and model generation. readme doesn't include info about running postgres locally. there is no make formula for postgres. address these issues.


this project also needs redis. create deployment manifests and installation deployment scripts for redis in the same was as ./k8s/postgres. use /home/lsm/Nextcloud/k3s-cluster/redis/ as a reference as this is the currently used redis cache. create this one in the llmmll namespace though. the redis instance in the redis namespace can be deleted.