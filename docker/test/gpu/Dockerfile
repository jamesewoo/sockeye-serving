FROM jwoo11/sockeye-serving:latest-gpu

USER root
WORKDIR /home/serving

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -O http://data.statmt.org/wmt17/translation-task/preprocessed/de-en/corpus.tc.de.gz \
    && curl -O http://data.statmt.org/wmt17/translation-task/preprocessed/de-en/corpus.tc.en.gz \
    && gunzip corpus.tc.de.gz \
    && gunzip corpus.tc.en.gz \
    && curl http://data.statmt.org/wmt17/translation-task/preprocessed/de-en/dev.tgz | tar xz

RUN pipenv run subword-nmt learn-joint-bpe-and-vocab \
        --input corpus.tc.de corpus.tc.en \
        -s 30000 \
        -o bpe.codes \
        --write-vocabulary bpe.vocab.de bpe.vocab.en

RUN pipenv run subword-nmt apply-bpe -c bpe.codes --vocabulary bpe.vocab.de --vocabulary-threshold 50 < corpus.tc.de > corpus.tc.BPE.de \
    && pipenv run subword-nmt apply-bpe -c bpe.codes --vocabulary bpe.vocab.en --vocabulary-threshold 50 < corpus.tc.en > corpus.tc.BPE.en \
    && pipenv run subword-nmt apply-bpe -c bpe.codes --vocabulary bpe.vocab.de --vocabulary-threshold 50 < newstest2016.tc.de > newstest2016.tc.BPE.de \
    && pipenv run subword-nmt apply-bpe -c bpe.codes --vocabulary bpe.vocab.en --vocabulary-threshold 50 < newstest2016.tc.en > newstest2016.tc.BPE.en

ENV LD_LIBRARY_PATH /usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

RUN pipenv run sockeye-prepare-data \
        -s corpus.tc.BPE.de \
        -t corpus.tc.BPE.en \
        -o train_data

RUN pipenv run python3 -m sockeye.train \
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

COPY test.sh .

ENTRYPOINT ["./test.sh"]
CMD ["test"]

LABEL version="2.0.0" \
      maintainer="james.e.woo@gmail.com" \
      source="https://github.com/jamesewoo/sockeye-serving" \
      description="A containerized service for neural machine translation"
