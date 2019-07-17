#!/usr/bin/env bash
set -e

if (( $# != 2 )); then
    echo "usage: $0 DOCKER_USER VERSION"
    exit 1
fi

docker_user="$1"
version="$2"

release() {
    if (( $# != 2 )); then
        echo "usage: release SOURCE ALIAS"
        exit 1
    fi

    local source="$1"
    local alias="$2"

    docker tag "$source" "$alias"
    docker tag "$source" "$docker_user/$source"
    docker tag "$alias" "$docker_user/$alias"
    docker push "$docker_user/$source"
    docker push "$docker_user/$alias"
}

release "sockeye-serving:$version" "sockeye-serving:latest"
release "sockeye-serving:$version-gpu" "sockeye-serving:latest-gpu"
