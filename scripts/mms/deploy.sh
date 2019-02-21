#!/usr/bin/env bash

# custom handler properties

# language to translate
lang="zh"
# Python package.module:function
handler="services.zh_handler:handle"

# model-archiver properties

model_name="${lang}"
# where the MAR will be saved
export_path="/tmp/models"
# where the model files live
model_path="${export_path}/${model_name}"

# Docker properties

# predictions API port
pred_port=8080
# management API port
mgmt_port=8081
pred_url="http://localhost:${pred_port}"
mgmt_url="http://localhost:${mgmt_port}"

model_url="${model_name}"
#model_url="${model_name}.mar"
#model_url="https://www.dropbox.com/s/pk7hmp7a5zjcfcj/zh.mar?dl=1"

if [[ "$1" = "update" ]]; then
    # update the scripts and handler files
    mkdir -p ${model_path}/scripts
    cp -r scripts/joshua/* ${model_path}/scripts
    cp -r scripts/moses/* ${model_path}/scripts
    cp -r src/services ${model_path}
    model-archiver -f --runtime python3 --export-path ${export_path} \
        --model-name ${model_name} --model-path ${model_path} --handler ${handler}
fi

# restart the Docker container
docker kill mms
docker rm mms
docker run -itd --name mms -p ${pred_port}:8080 -p ${mgmt_port}:8081 \
    -v ${export_path}:/opt/ml/model jwoo11/sockeye-serving

# load a model
until curl -X POST "${mgmt_url}/models?synchronous=true&initial_workers=1&url=${model_url}"
do
  echo "Waiting for initialization..."
  sleep 1
done

# test prediction
curl -X GET "${mgmt_url}/models/${model_name}"
curl -X POST "${pred_url}/predictions/${model_name}" -H "Content-Type: application/json" \
    -d '{ "text": "我的世界是一款開放世界遊戲，玩家沒有具體要完成的目標，即玩家有超高的自由度選擇如何玩遊戲" }' &
