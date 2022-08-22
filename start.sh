#!/bin/bash
source .env

SERVER_KEY="server.key"
SERVER_PEM="server.pem"
CLIENT_PEM="client.pem"
python3 -m trustme -i service1

cp $SERVER_KEY images/service/src
cp $SERVER_PEM  images/service/src
cp $CLIENT_PEM  images/client/src

echo "Start docker compose"
docker-compose --env-file .env up -d --build

echo "Copying the Cribl Configuration"
docker cp cribl/ cribl1:/opt/cribl/local/

echo "Waiting for the kibana to start"

counter=0
limit=10

until $(curl --output /dev/null --silent --head --fail http://localhost:$KIBANA_HOST_PORT); do
    if [ ${counter} -eq ${limit} ];then
      printf '\n'
      echo "Max attempts reached"
      exit 1
    fi

    printf '.'
    counter=$(($counter+1))
    sleep 5
done

printf '\n'
echo "Copying the kibana Configuration"
curl -X POST http://localhost:$KIBANA_HOST_PORT/api/saved_objects/_import?overwrite=true -H "kbn-xsrf: true" --form file=@$KIBANA_CFG_FILE

echo "Demo is ready."
