# prge bgm
prge demo app by student


### How To Start

```bash
docker-compose -f ./docker-compose/docker-compose-prge-local.yml --env-file .env -p local-prge up --build -d
```

### Other Commands
Composes only FastAPI
```bash
docker-compose -f ./docker-compose/docker-compose-prge-local.yml --env-file .env -p local-prge up --build -d fastapi
```
Stops and removes all containers, networks, and images defined
```bash
docker-compose -f ./docker-compose/docker-compose-prge-local.yml down -v
```
Forces the removal of all unused containers, networks, and images
```bash
docker system prune -a -f
```
Removes all unused local volumes and unreferenced data
```bash
docker system prune --volumes
```
Opens an interactive terminal session inside the running prge_2025_geoserver container
```bash
doccker exec -it prge_2025_geoserver bash
```