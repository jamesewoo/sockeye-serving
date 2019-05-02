# sockeye-serving
`sockeye-serving` is a containerized service for neural machine translation that uses Amazon's `sockeye` framework as the translation engine.
The web server makes use of `mxnet-model-server`, which provides a management API for loading models and a prediction API for requesting translations.

Any Sockeye model can be loaded via the management API.
Text preprocessing is built into the request pipeline and supports a wide variety of languages.
Specialized processing for specific languages can be implemented using custom handlers.

## Quickstart
This example shows how to serve an existing model for Chinese to English translation.
First, pull the latest Docker image:
```bash
docker pull jwoo11/sockeye-serving
```

Download the example model archive (MAR).
This is a ZIP archive containing the parameter files and scripts needed to run translation:
* https://www.dropbox.com/s/pk7hmp7a5zjcfcj/zh.mar?dl=0

Extract the MAR file to `/tmp/models`.
 This directory will be the source for a bind mount for Docker:
```bash
unzip -d /tmp/models/zh zh.mar
```

Start the server:
```bash
docker run -itd --name sockeye_serving -p 8080:8080 -p 8081:8081 -v /tmp/models:/opt/ml/model jwoo11/sockeye-serving
```

Now, load the model using the management API. Note that the URL of the model is relative to the bind mount:
```bash
curl -X POST "http://localhost:8081/models?synchronous=true&initial_workers=1&url=zh"
```
Get the status of the model with the following:
```bash
curl -X GET "http://localhost:8081/models/zh"
```
The response should look like this:
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

A better model trained on more data returns this response:
```json
{
  "translation": "My world is an open world game, and players have no specific goal to accomplish, that is, players have a high degree of freedom to choose how to play."
}
```

## Installation
To install `sockeye-serving` run the following in a virtual environment:
```bash
pip install sockeye-serving
```
If you want to install from source, a `Pipfile` is provided.
Clone the repository and run `pipenv install`.

Installation places the command line interfaces `sockeye-serving` and `sockeye-client` on your virtual environment's path.

## Command Line Interfaces
You can use `sockeye-serving` to easily start Docker and to make REST calls to both the management and prediction APIs.
First, a configuration file must be placed in either the current directory or some place referenced by `SOCKEYE_SERVING_CONF`.
Example properties are located in `config/sockeye-serving.conf`.
Here's some basic usage:
```bash
# start the Docker container
sockeye-serving start

# deploy a model
sockeye-serving deploy zh

# list available models
sockeye-serving list

# translate text
sockeye-serving translate zh "my text"

# upload a file for translation
sockeye-serving upload zh "my_file.txt"
```
Run `sockeye-serving help` for a full list of commands.

The Python client takes a YAML configuration file.
An example configuration is in `config/sockeye-client.yml`. 
This client does not support restarting Docker, however, it does exercise the full API provided by `mxnet-model-server`.
The commands which accept query parameters are below:
```bash
$ sockeye-client deploy -h
usage: sockeye-client deploy [-h] [-m MODEL_NAME] [-x HANDLER] [-r RUNTIME]
                             [-b BATCH_SIZE] [-d MAX_BATCH_DELAY]
                             [-i INITIAL_WORKERS] [-s] [-t RESPONSE_TIMEOUT]
                             url
...

$ sockeye-client list -h
usage: sockeye-client list [-h] [-l LIMIT] [-t NEXT_PAGE_TOKEN]
...

$ sockeye-client scale -h
usage: sockeye-client scale [-h] [-a MIN_WORKER] [-b MAX_WORKER]
                            [-n NUMBER_GPU] [-s] [-t TIMEOUT]
                            model_name
...
```
Run `sockeye-client -h` to show a full list of commands. 
For more information on the API, see [additional documentation](#additional-documentation) for `mxnet-model-server`.

## Jupyter Notebook
If you want to translate text with Jupyter, you can use `notebooks/machine_translation.ipynb`.
Make sure `requests` is installed in your Python environment.

## Choosing between CPUs and GPUs
`sockeye-serving` provides two Dockerfiles, one for CPUs and one for GPUs.
You can easily configure which tag to use in your `sockeye-serving.conf` file.
If using GPUs, you should set `docker_exec="nvidia-docker"`

For CPUs, you must ensure that each model directory contains a `sockeye-args.txt` with the flag `--use-cpu`.
After changing the file, redeploy the model. Restarting Docker is not necessary.

## Enabling TLS
The provided configuration instructs the server to use plain HTTP.
To enable TLS, you can either supply a Java keystore or a private key and certificate in PEM format.

Using `config/config.properties` as a starting point, create a new `config.properties` file and save it under `/tmp/models`:
```properties
model_store=/opt/ml/model
inference_address=https://0.0.0.0:8443
management_address=https://0.0.0.0:8444
```
Suppose you have a key pair residing on the host at `/path/to/certs`.
Set the properties for the keystore:
```properties
keystore=/path/to/certs/keystore.p12
keystore_pass=changeit
keystore_type=PKCS12
```
Or provide the path to the server's private key and certificate:
```properties
private_key_file=/path/to/certs/private.key
certificate_file=/path/to/certs/cert.pem
```
Then start the container:
```bash
docker run -itd --name sockeye_serving -p 8443:8443 -p 8444:8444 \
    -v /path/to/certs:/path/to/certs \
    -v /tmp/models:/opt/ml/model jwoo11/sockeye-serving \
    mxnet-model-server --start --mms-config /opt/ml/model/config.properties
```

To make requests using `curl` you should ensure that you set `--cert`, `--key`, and `--cacert` as needed.

## <a name="additional-documentation"></a> Additional Documentation

For more information on `mxnet-model-server`, see:
* https://github.com/awslabs/mxnet-model-server/tree/master/docs
