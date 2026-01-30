# prge bgm
prge demo app by student


### how to start

```bash
docker-compose -f ./docker-compose/docker-compose-prge-local.yml --env-file .env -p local-prge up --build -d
```
```bash
docker system prune -a -f
```
```bash
docker system prune --volumes
```

```bash
doccker exec -it prge_2025_geoserver bash
```