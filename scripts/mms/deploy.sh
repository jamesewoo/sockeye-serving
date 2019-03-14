#!/usr/bin/env bash

# Docker properties
# =====
# predictions API port on the host
pred_port=8080
# management API port on the host
mgmt_port=8081
pred_url="http://localhost:${pred_port}"
mgmt_url="http://localhost:${mgmt_port}"
# location of models on the host
export_path="/tmp/models"

function restart_docker {
    docker rm -f mms
    docker run -itd --name mms -p ${pred_port}:8080 -p ${mgmt_port}:8081 \
        -v ${export_path}:/opt/ml/model jwoo11/sockeye-serving
}

function load_model {
    local model_url=$1

    until curl -X POST "${mgmt_url}/models?synchronous=true&initial_workers=1&url=${model_url}"
    do
      echo "Waiting for initialization..."
      sleep 1
    done
}

function test_prediction {
    local model_name=$1

    curl -X GET "${mgmt_url}/models/${model_name}"
    curl -X POST "${pred_url}/predictions/${model_name}" -H "Content-Type: application/json" \
        -d '{ "text": "我的世界是一款開放世界遊戲，玩家沒有具體要完成的目標，即玩家有超高的自由度選擇如何玩遊戲" }'
}

function update_model {
    if [[ -z $(command -v model-archiver) ]]; then
        echo "model-archiver not found - is virtualenv activated?"
        exit 127
    fi

    local model_path=$1
    local model_name=$2
    local handler=$3

    # update the scripts and handler files in the export path
    mkdir -p "${model_path}/scripts"
    cp config/sockeye-args.txt "${model_path}"
    cp -r scripts/joshua/* "${model_path}/scripts"
    cp -r scripts/moses/* "${model_path}/scripts"
    cp -r src/services "${model_path}"

    # create a new MAR from the updated model files
    model-archiver -f --runtime python3 --export-path "${export_path}" \
        --model-name "${model_name}" --model-path "${model_path}" --handler "${handler}"
    # update manifest file in original directory
    unzip -uo "${model_path}.mar" -d "${model_path}"
}

function deploy_model {
    # language to translate
    local lang=$1
    # Python package.module:function
    local handler=$2
    # optional command
    local cmd=$3
    # name of the model
    local model_name="${lang}"
    # where the model files live
    local model_path="${export_path}/${model_name}"

    # URL of the model relative to the export path
    local model_url="${model_name}"
    #local model_url="${model_name}.mar"
    #local model_url="https://www.dropbox.com/s/pk7hmp7a5zjcfcj/zh.mar?dl=1"

    if [[ "${cmd}" = "update" ]]; then
        update_model "${model_path}" "${model_name}" "${handler}"
    fi

    load_model "${model_url}"

    test_prediction "${model_name}"
}

# optional command
cmd=$1
restart_docker
deploy_model zh services.zh_handler:handle "${cmd}"
