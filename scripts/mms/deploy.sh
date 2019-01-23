#!/usr/bin/env bash

cp -r src/services /tmp/models/zh
model-archiver -f --runtime python3 --export-path /tmp/models/ \
    --model-name zh --model-path /tmp/models/zh --handler services.sockeye_service:handle

docker kill mms && docker rm mms
docker run -itd --name mms -p 8080:8080  -p 8081:8081 -v /tmp/models/:/models jwoo11/sockeye-serving \
    mxnet-model-server --start --mms-config /models/config.properties

until curl -X POST "http://localhost:8081/models?url=zh.mar"
do
  echo "Waiting for initialization..."
  sleep 1
done

curl -X PUT "http://localhost:8081/models/zh?min_worker=1"
curl -X GET "http://localhost:8081/models/zh"
curl -X POST "http://localhost:8080/predictions/zh" -H "Content-Type: application/json" \
    -d '{ "text": "我的世界是一款開放世界遊戲，玩家沒有具體要完成的目標，即玩家有超高的自由度選擇如何玩遊戲" }' &
curl -X POST "http://localhost:8080/predictions/zh" -H "Content-Type: application/json" \
    -d '"我的世界是一款開放世界遊戲，玩家沒有具體要完成的目標，即玩家有超高的自由度選擇如何玩遊戲"' &
curl -X POST "http://localhost:8080/predictions/zh" -T "data/sample.txt" &
