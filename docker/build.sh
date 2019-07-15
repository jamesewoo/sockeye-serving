#!/usr/bin/env bash
set -e

if [ "$#" -ne 1 ]; then
    echo "usage: $0 SOCKEYE_SERVING_HOME"
    exit 1
fi

sockeye_serving_home="$1"
docker_user=jwoo11
models_dir=/tmp/models

tag_and_push() {
    if (( $# != 1 )); then
        echo "usage: tag_and_push TAG"
        exit 1
    fi

    docker tag $tag "$docker_user/$tag"
    docker push "$docker_user/$tag"
}

cd "$sockeye_serving_home"

tag=sockeye-serving:latest
docker build -t $tag -f docker/cpu/Dockerfile .
tag_and_push $tag

tag=sockeye-serving:latest-gpu
docker build -t $tag -f docker/gpu/Dockerfile .
tag_and_push $tag

tag=sockeye-serving:test
docker build -t $tag -f docker/test/cpu/Dockerfile docker/test
# run the test image - requires a "de" model in $models_dir
docker run -itd --name sockeye_serving -p 8080:8080 -p 8081:8081 -v "$models_dir":/opt/ml/model sockeye-serving:test
until curl -X POST "http://localhost:8081/models?synchronous=true&initial_workers=1&url=de"; do
  echo "Waiting for initialization..."
  sleep 1
done
curl -X GET "http://localhost:8081/models/de"
curl -X POST "http://localhost:8080/predictions/de" -H "Content-Type: application/json" \
    -d '{ "text": "er ist so ein toller Kerl und ein Familienvater ." }'
docker stop sockeye_serving
tag_and_push $tag

tag=sockeye-serving:test-gpu
docker build -t $tag -f docker/test/gpu/Dockerfile docker/test
tag_and_push $tag
