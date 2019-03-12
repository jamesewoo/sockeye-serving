# sockeye-serving
`sockeye-serving` is a containerized service for neural machine translation that uses Amazon's `sockeye` framework as the translation engine.
The web server is implemented by Amazon's `mxnet-model-server`, which provides a management API for loading models and a prediction API for requesting translations.

Any Sockeye model can be loaded via the management API.
Text preprocessing is built into the request pipeline and supports a wide variety of languages.
Specialized processing for specific languages can be implemented using custom Python handlers.

## Getting Started With Docker
This example shows how to serve an existing model for Chinese to English translation.
First, pull the latest Docker image:
```bash
docker pull jwoo11/sockeye-serving
```

Download the example model archive file (MAR).
This is a ZIP archive containing the parameter files and scripts needed to run translation for a particular language:
* https://www.dropbox.com/s/pk7hmp7a5zjcfcj/zh.mar?dl=0

Extract the MAR file to `/tmp/models`.
 We'll use this directory as a bind mount for Docker:
```bash
unzip -d /tmp/models/zh zh.mar
```

Start the server:
```bash
docker run -itd --name mms -p 8080:8080 -p 8081:8081 -v /tmp/models:/opt/ml/model jwoo11/sockeye-serving
```

Now we can load the model using the management API. Note that the URL of the model is relative to the bind mount:
```bash
curl -X POST "http://localhost:8081/models?synchronous=true&initial_workers=1&url=zh"
```
Get the status of the model with the following:
```bash
curl -X GET "http://localhost:8081/models/zh"
```
```json
{
  "modelName": "zh",
  "modelUrl": "zh",
  "runtime": "python3",
  "minWorkers": 1,
  "maxWorkers": 1,
  "batchSize": 1,
  "maxBatchDelay": 100,
  "workers": [
    {
      "id": "9000",
      "startTime": "2019-01-26T00:49:10.431Z",
      "status": "READY",
      "gpu": false,
      "memoryUsage": 601395200
    }
  ]
}
```

To translate text use the inference API. Notice that the port is different from above. 
```bash
curl -X POST "http://localhost:8080/predictions/zh" -H "Content-Type: application/json" \
    -d '{ "text": "我的世界是一款開放世界遊戲，玩家沒有具體要完成的目標，即玩家有超高的自由度選擇如何玩遊戲" }'
```

The translation quality depends on the model. The provided model returns this translation:
```json
{
  "translation": "in my life was a life of a life of a public public, and a public, a time, a video, a play, which, it was a time of a time of a time."
}
```

Our latest model returns this response:
```json
{
  "translation": "My world is an open world game, and players have no specific goal to accomplish, that is, players have a high degree of freedom to choose how to play."
}
```

For more information on MAR files and the built-in REST APIs, see:
* https://github.com/awslabs/mxnet-model-server/tree/master/docs
