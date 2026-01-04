#!/bin/bash
git pull

# Stop and remove the current Docker Compose services
sudo docker-compose down

# sudo docker volume rm $(sudo docker volume ls -q)

# Build and recreate the Docker Compose services in detached mode
sudo docker-compose up --force-recreate --build -d

# Prune unused Docker images
sudo docker image prune -f

# Stop Docker service and Docker socket
sudo systemctl stop docker
sudo systemctl stop docker.socket

# Start Docker service and Docker socket
sudo systemctl start docker
sudo systemctl start docker.socket
