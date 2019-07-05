#!/usr/bin/env bash
set -e

if [ "$1" = 'train' ]; then

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
        --device-ids -1 \
        -o wmt_model

elif [ "$1" = 'test' ]; then

    echo "er ist so ein toller Kerl und ein Familienvater ." \
    | pipenv run subword-nmt apply-bpe \
        -c bpe.codes \
        --vocabulary bpe.vocab.en \
        --vocabulary-threshold 50 \
    | pipenv run sockeye-translate -m wmt_model \
    | sed -r 's/@@( |$)//g'

else
    exec "$@"
fi
