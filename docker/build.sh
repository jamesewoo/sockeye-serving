#!/usr/bin/env bash
set -e

if [ "$#" -ne 1 ]; then
    echo "usage: build.sh SOCKEYE_SERVING_HOME"
    exit 1
fi

sockeye_serving_home="$1"
docker_user=jwoo11

cd "$sockeye_serving_home"

docker build -t sockeye-serving:latest -f docker/cpu/Dockerfile .
docker build -t sockeye-serving:latest-gpu -f docker/gpu/Dockerfile .

docker tag sockeye-serving:latest "$docker_user/sockeye-serving:latest"
docker tag sockeye-serving:latest-gpu "$docker_user/sockeye-serving:latest-gpu"

docker push "$docker_user/sockeye-serving:latest"
docker push "$docker_user/sockeye-serving:latest-gpu"
