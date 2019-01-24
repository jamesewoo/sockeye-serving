# sockeye-serving
Sockeye server based on mxnet-model-server

## Getting Started With Docker
Pull the latest Docker image:
```bash
docker pull jwoo11/sockeye-serving
```

Download the example model files:
* https://www.dropbox.com/s/j2xuqdrv9ygean0/config.properties?dl=0
* https://www.dropbox.com/s/pk7hmp7a5zjcfcj/zh.mar?dl=0

Extract the files to a model directory:
```bash
mkdir -p /tmp/models/zh
mv config.properties /tmp/models
unzip -d /tmp/models/zh zh.mar
```

Start the server:
```bash
docker run -itd --name mms -p 8080:8080  -p 8081:8081 -v /tmp/models/:/models jwoo11/sockeye-serving \
    mxnet-model-server --start --mms-config /models/config.properties
```

Copy the BPE codes into the container:
```bash
docker exec mms mkdir -p data
docker cp /tmp/models/zh/bpe.codes.zh-en mms:/home/model-server/data/
```
Try making some requests:
```bash
until curl -X POST "http://localhost:8081/models?url=zh"
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
```
