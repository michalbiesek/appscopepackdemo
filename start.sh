#!/bin/bash
source .env

echo "Start docker compose"
docker-compose --env-file .env up -d --build

echo "Copying the Cribl Configuration"
docker cp cribl/ cribl01:/opt/cribl/local/

echo "Demo is ready."
