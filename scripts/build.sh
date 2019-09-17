#!/usr/bin/env bash
set -e

if (( $# != 2 )); then
    echo "usage: $0 SOCKEYE_SERVING_HOME VERSION"
    exit 1
fi

sockeye_serving_home="$1"
docker_user=jwoo11
version="$2"
training_output=/opt/data/wmt_model

export SOCKEYE_SERVING_CONF="$sockeye_serving_home/config/sockeye-serving.conf"

create_model() {
    if (( $# != 2 )); then
        echo "usage: create_model SRC DEST"
        exit 1
    fi

    local src="$1"
    local dest="$2"

    (cd "$src" \
        && mkdir -p "$dest" \
        && cp -L args.yaml config params.best symbol.json version vocab* "$dest")

    cp "$sockeye_serving_home/docker/test/resources/bpe-codes.txt" "$dest"
    pipenv run sockeye-serving update de config/sockeye/cpu/sockeye-args.txt
    pipenv run sockeye-serving archive de default_handler
}

test_server() {
    if (( $# != 2 )); then
        echo "usage: test_server MODELS_DIR IMAGE"
        exit 1
    fi

    local models_dir="$1"
    local image="$2"

    docker run -itd --name sockeye_serving_test -p 8080:8080 -p 8081:8081 -v "$models_dir":/opt/ml/model "$image"

    until curl -X POST "http://localhost:8081/models?synchronous=true&initial_workers=1&url=de"; do
      echo "Waiting for initialization..."
      sleep 1
    done
    curl -X GET "http://localhost:8081/models/de"
    curl -X POST "http://localhost:8080/predictions/de" -H "Content-Type: application/json" \
        -d '{ "text": "er ist so ein toller Kerl und ein Familienvater ." }'
    curl -X POST "http://localhost:8080/predictions/de" -H "Content-Type: application/json" \
        -d '{ "text": "er ist so ein toller Kerl und ein Familienvater .", "constraints": ["toller"] }'
    curl -X POST "http://localhost:8080/predictions/de" -H "Content-Type: application/json" \
        -d '{ "text": "er ist so ein toller Kerl und ein Familienvater .", "avoid": ["toller"] }'

    docker logs sockeye_serving_test > "$image".log
    docker rm -f sockeye_serving_test
}

tag_and_push() {
    if (( $# != 2 )); then
        echo "usage: tag_and_push DOCKER_USER TAG"
        exit 1
    fi

    local docker_user="$1"
    local tag="$2"

    docker tag $tag "$docker_user/$tag"
    docker push "$docker_user/$tag"
}

cd "$sockeye_serving_home"

pipenv run pytest

# create a model from training output
create_model "$training_output" /tmp/models/de

tag="sockeye-serving:$version"
docker build -t "$tag" -f docker/cpu/Dockerfile .
test_server /tmp/models "$tag"
tag_and_push "$docker_user" "$tag"

tag="sockeye-serving:$version-gpu"
docker build -t "$tag" -f docker/gpu/Dockerfile .
# need libcuda to test on GPU
# test_server /tmp/models "$tag"
tag_and_push "$docker_user" "$tag"

# prepare PyPI release
rm -rf build/ dist/
python3 setup.py sdist bdist_wheel
