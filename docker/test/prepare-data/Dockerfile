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

RUN head -n 200000 corpus.tc.BPE.de > corpus.tc.BPE.de.tmp && mv corpus.tc.BPE.de.tmp corpus.tc.BPE.de \
    && head -n 200000 corpus.tc.BPE.en > corpus.tc.BPE.en.tmp && mv corpus.tc.BPE.en.tmp corpus.tc.BPE.en

COPY test.sh .

ENTRYPOINT ["./test.sh"]
CMD ["test"]

LABEL version="2.1.0" \
      maintainer="james.e.woo@gmail.com" \
      source="https://github.com/jamesewoo/sockeye-serving" \
      description="A containerized service for neural machine translation"
