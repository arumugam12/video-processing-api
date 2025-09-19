set -e

export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=videodb
export CLOUD_ENV=production


echo "Building and starting Docker containers..."
docker-compose pull
docker-compose build
docker-compose up -d

echo "Waiting for services to start..."
sleep 10

echo "Running database migrations..."
docker-compose exec backend alembic upgrade head

echo "Deployment complete!"
echo "API should be available at http://<your-cloud-ip>:8000/"
