# Smartplyalist API

Built with: <https://fastapi.tiangolo.com/>

## Development

1. Build the container: `docker build --no-cache -t jkulak/smartplaylist-api ./api`
2. Run the container: `docker run -ti --rm --name smartplaylist-api --env-file .env -v $(pwd)/api/src:/api -p 8008:8008 jkulak/smartplaylist-api`

Open:

* <http://localhost:8008/> for the API
* <http://localhost:8008/docs> for Swagger documentation
* <http://localhost:8008/redoc> for ReDoc documentation
