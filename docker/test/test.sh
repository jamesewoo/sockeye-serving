#!/usr/bin/env bash
set -e

train() {
    if (( $# != 1 )); then
        echo "usage: train DEVICE_LINE"
        exit 1
    fi

    $device_line="$1"

    pipenv run sockeye-prepare-data \
        -s corpus.tc.BPE.de \
        -t corpus.tc.BPE.en \
        -o train_data

    pipenv run python3 -m sockeye.train \
        -d train_data \
        -vs newstest2016.tc.BPE.de \
        -vt newstest2016.tc.BPE.en \
        --encoder rnn \
        --decoder rnn \
        --num-embed 256 \
        --rnn-num-hidden 512 \
        --rnn-attention-type dot \
        --max-seq-len 60 \
        --decode-and-evaluate 500 \
        "$device_line" \
        -o wmt_model
}

start_server() {
    cp bpe.codes /opt/ml/model/de/bpe-codes.txt
    pipenv run mxnet-model-server --start --mms-config config.properties
    tail -f /dev/null
}

if [ "$1" = 'train' ]; then

    train "--use-cpu"

elif [ "$1" = 'train-gpu' ]; then

    train "--device-ids -1"

elif [ "$1" = 'test' ]; then

    start_server

else
    exec "$@"
fi
