## For judges

1. I have not implemented the `GET /api/profit?from{{from}}&to={{to}}`
2. I have not implemented the `GET /api/top?from{{from}}&to={{to}}&top=100&by=profit`
3. All other endpoints are implemented and tested.

### Installation

**Build and Start the Services**

```bash
docker-compose up --build
```

This command will build the Docker images and start all services defined in the `docker-compose.yml` file. The API will be accessible at `http://localhost:8080/api`.


### Run tests
    
```bash
docker-compose run --rm project pytest
```
