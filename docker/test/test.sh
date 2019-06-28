#!/usr/bin/env bash
set -e

if [ "$1" = 'test' ]; then

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
