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

### Corner cases covered
1. Set limits for sku length (max: 128)
2. 