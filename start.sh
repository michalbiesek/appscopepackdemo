#!/bin/bash
source .env

PRIVATE_KEY_SERVER_NAME="domain.key"
CERT_SERVER_NAME="domain.crt"
PRIVATE_KEY_CLIENT_NAME="client.key"
CSR_CLIENT_NAME="cert.csr"
CERT_CLIENT_NAME="cert.pem"

openssl req -x509 -newkey rsa:4096 -nodes -out $CERT_SERVER_NAME -keyout $PRIVATE_KEY_SERVER_NAME -days 365 -subj "/C=PL/ST=Warsaw/L=GoatTown/O=Cribl/OU=Appscope/CN=service1"
openssl req -x509 -newkey rsa:4096 -nodes -out $CSR_CLIENT_NAME -keyout $PRIVATE_KEY_CLIENT_NAME -days 365 -subj "/C=PL/ST=Warsaw/L=GoatTown/O=Cribl/OU=Appscope/CN=client"
openssl req -x509 -in $CSR_CLIENT_NAME -CA $CERT_SERVER_NAME -CAkey P$RIVATE_KEY_SERVER_NAME -out $CERT_CLIENT_NAME -set_serial 01 -days 365

cp $PRIVATE_KEY_SERVER_NAME images/service/src
cp $CERT_SERVER_NAME  images/service/src
cp $CERT_CLIENT_NAME  images/client/src

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
