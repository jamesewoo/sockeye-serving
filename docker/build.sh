#!/usr/bin/env bash
set -e

if [ "$#" -ne 1 ]; then
    echo "usage: $0 SOCKEYE_SERVING_HOME"
    exit 1
fi

sockeye_serving_home="$1"
docker_user=jwoo11

cd "$sockeye_serving_home"

docker build -t sockeye-serving:latest -f docker/cpu/Dockerfile .
docker tag sockeye-serving:latest "$docker_user/sockeye-serving:latest"
docker push "$docker_user/sockeye-serving:latest"

docker build -t sockeye-serving:test -f docker/test/cpu/Dockerfile docker/test
docker tag sockeye-serving:test "$docker_user/sockeye-serving:test"
docker push "$docker_user/sockeye-serving:test"
