#!/bin/bash
source .env

KEY_CERT_DIR="/opt/"
PRIVATE_KEY_NAME="domain.key"
CERT_NAME="domain.crt"

#######################################
# Copy private key to specific docker container
# Arguments:
#   Name of the docker container
#######################################
copy_key () {
    local output_dir=$1:$KEY_CERT_DIR

    echo "Copying the TLS private key to $output_dir"
    docker cp $PRIVATE_KEY_NAME $output_dir$PRIVATE_KEY_NAME
}

#######################################
# Generate ssh key
# Arguments:
#   Username
#######################################
ssh_new_keys () {
    local user_name=$1
    local key_name=${user_name}_key
    local pub_key=${key_name}.pub

    echo "Generate key $key_name"

    ssh-keygen -q -t rsa -b 4096 -f $key_name -P ""
    cp $pub_key images
}

#######################################
# Delete duplicate public key
# Arguments:
#   Username
#######################################
ssh_rm_dup_public_key () {
    local pub_key=${1}_key.pub

    echo "Remove key $pub_key"

    rm images/${pub_key}
}

#######################################
# Copy certificate to specific docker container
# Arguments:
#   Name of the docker container
#######################################
copy_cert () {
    local output_dir=$1:$KEY_CERT_DIR

    echo "Copying the TLS certificate to $output_dir"
}

# echo "Start generate private & public keys"
# ssh_new_keys "foouser" "appscope_sshd" 
# ssh_new_keys "baruser" "appscope_sshd"
# cp foouser_key.pub evil_machine/eviluser_key.pub


# VM_COUNT=`sysctl -n vm.max_map_count`

# echo "Checking virtual memory settings"

# if [ $VM_COUNT -lt $VM_EXPECTED_LIMIT ];then
#     echo "Error with vm.max_map_count settings value $VM_COUNT it too low"
#     echo "Please change the limit with: 'sudo sysctl -w vm.max_map_count=$VM_EXPECTED_LIMIT'"
#     exit 1
# fi

echo "Start docker compose"
docker-compose --env-file .env up -d --build

echo "Copying the Cribl Configuration"
docker cp cribl/ cribl1:/opt/cribl/local/

# echo "Waiting for the kibana to start"

# counter=0
# limit=10

# until $(curl --output /dev/null --silent --head --fail http://localhost:$KIBANA_HOST_PORT); do
#     if [ ${counter} -eq ${limit} ];then
#       printf '\n'
#       echo "Max attempts reached"
#       exit 1
#     fi

#     printf '.'
#     counter=$(($counter+1))
#     sleep 5
# done

# printf '\n'
# echo "Copying the kibana Configuration"
# curl -X POST http://localhost:$KIBANA_HOST_PORT/api/saved_objects/_import?overwrite=true -H "kbn-xsrf: true" --form file=@$KIBANA_CFG_FILE

echo "Demo is ready."
