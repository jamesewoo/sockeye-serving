#!/usr/bin/env bash
set -e

if (( $# != 1 )); then
    echo "usage: $0 SOCKEYE_SERVING_HOME"
    exit 1
fi

sockeye_serving_home="$1"
docker_user=jwoo11
version=2.1.0

export SOCKEYE_SERVING_CONF="$sockeye_serving_home/config/sockeye-serving.conf"

create_model() {
    if (( $# != 2 )); then
        echo "usage: create_model SRC DEST"
        exit 1
    fi

    local src="$1"
    local dest="$2"

    (cd "$src" \
        && mkdir -p "$dest/de" \
        && cp -L args.yaml config params.best symbol.json version vocab* "$dest/de")

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

    docker run -itd --name sockeye_serving -p 8080:8080 -p 8081:8081 -v "$models_dir":/opt/ml/model "$image"

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

tag="sockeye-serving:$version-devel"
docker build -t "$tag" -f docker/cpu/Dockerfile .
tag_and_push "$docker_user" "$tag"

tag="sockeye-serving:$version-gpu-devel"
docker build -t "$tag" -f docker/gpu/Dockerfile .
tag_and_push "$docker_user" "$tag"

tag=sockeye-serving:test
docker build -t $tag -f docker/test/cpu/Dockerfile docker/test
create_model /opt/data/wmt_model /tmp/models
test_server /tmp/models "$tag"
tag_and_push "$docker_user" "$tag"

tag=sockeye-serving:test-gpu
docker build -t "$tag" -f docker/test/gpu/Dockerfile docker/test
tag_and_push "$docker_user" "$tag"

# prepare PyPI release
rm -rf build/ dist/
python3 setup.py sdist bdist_wheel
