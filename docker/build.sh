#!/usr/bin/env bash
set -e

if [ "$#" -ne 1 ]; then
    echo "usage: $0 SOCKEYE_SERVING_HOME"
    exit 1
fi

sockeye_serving_home="$1"
docker_user=jwoo11
version=2.0.0
model_src=/opt/data/wmt_model
model_dest=/tmp/models

export SOCKEYE_SERVING_CONF="$sockeye_serving_home/config/sockeye-serving.conf"

create_model() {
    if (( $# != 2 )); then
        echo "usage: copy_model SRC DEST"
        exit 1
    fi

    src="$1"
    dest="$2"

    (cd "$src" \
        && mkdir -p "$dest/de" \
        && cp -L args.yaml config params.best symbol.json version vocab* "$dest/de")

    pipenv run sockeye-serving update de config/sockeye/cpu/sockeye-args.txt
    pipenv run sockeye-serving archive de default_handler
}

test_server() {
    create_model "$model_src" "$model_dest"

    docker run -itd --name sockeye_serving -p 8080:8080 -p 8081:8081 -v "$model_dest":/opt/ml/model sockeye-serving:test

    until curl -X POST "http://localhost:8081/models?synchronous=true&initial_workers=1&url=de"; do
      echo "Waiting for initialization..."
      sleep 1
    done
    curl -X GET "http://localhost:8081/models/de"
    curl -X POST "http://localhost:8080/predictions/de" -H "Content-Type: application/json" \
        -d '{ "text": "er ist so ein toller Kerl und ein Familienvater ." }'

    docker stop sockeye_serving
}

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
test_server
tag_and_push $tag

tag=sockeye-serving:test-gpu
docker build -t $tag -f docker/test/gpu/Dockerfile docker/test
tag_and_push $tag

# prepare Docker release
tag=sockeye-serving:"$version"
docker tag sockeye-serving:latest "$tag"
tag_and_push $tag
# GPU version
tag=sockeye-serving:"$version-gpu"
docker tag sockeye-serving:latest-gpu "$tag"
tag_and_push $tag

# prepare PyPI release
rm -rf build/ dist/
python3 setup.py sdist bdist_wheel
