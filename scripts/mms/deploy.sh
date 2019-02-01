#!/usr/bin/env bash

if [[ "$1" = "update" ]]; then
    cp -r src/services /tmp/models/zh
    model-archiver -f --runtime python3 --export-path /tmp/models/ \
        --model-name zh --model-path /tmp/models/zh --handler services.sockeye_service:handle
fi

docker kill mms
docker rm mms
docker run -itd --name mms -p 8080:8080 -p 8081:8081 -v /tmp/models:/opt/ml/model jwoo11/sockeye-serving serve

#URL="zh.mar"
URL="zh"
#URL="https://www.dropbox.com/s/pk7hmp7a5zjcfcj/zh.mar?dl=1"

until curl -X POST "http://localhost:8081/models?synchronous=true&initial_workers=1&url=${URL}"
do
  echo "Waiting for initialization..."
  sleep 1
done

curl -X GET "http://localhost:8081/models/zh"
curl -X POST "http://localhost:8080/predictions/zh" -H "Content-Type: application/json" \
    -d '{ "text": "我的世界是一款開放世界遊戲，玩家沒有具體要完成的目標，即玩家有超高的自由度選擇如何玩遊戲" }' &
#curl -X POST "http://localhost:8080/predictions/zh" -H "Content-Type: application/json" \
#    -d '"我的世界是一款開放世界遊戲，玩家沒有具體要完成的目標，即玩家有超高的自由度選擇如何玩遊戲"' &
#curl -X POST "http://localhost:8080/predictions/zh" -T "data/sample.txt" &
