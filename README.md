# prge bgm
prge demo app by student


### How To Start

```bash
docker-compose -f ./docker-compose/docker-compose-prge-local.yml --env-file .env -p local-prge up --build -d
```

### Other Commands

```bash
docker-compose -f ./docker-compose/docker-compose-prge-local.yml down -v
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