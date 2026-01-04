#!/bin/bash
export PGPASSWORD=$POSTGRES_PASSWORD
pg_dump -h localhost -U agaba_user -W agaba_db --no-password > ../../db/docker-entrypoint-initdb.d/agaba_db_init.sql

# echo "Initial database sent to db container successfully"

sudo -S docker-compose down -v &&
sudo docker-compose up --force-recreate --build -d &&
sudo docker image prune -f

echo "Docker containers recreated successfully"
