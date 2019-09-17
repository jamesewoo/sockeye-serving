FROM nvidia/cuda:10.1-cudnn7-runtime

RUN useradd -m serving \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        python3-dev \
        python3-pip \
        openjdk-8-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

USER serving

ENV HOME /home/serving
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PATH "$PATH:$HOME/.local/bin"
ENV PYTHONUNBUFFERED TRUE
ENV SOCKEYE_VERSION=1.18.106

WORKDIR $HOME

COPY docker/gpu/Pipfile .
RUN pip3 install --user -U pip pipenv \
    && pipenv run pip install --no-cache-dir --no-deps sockeye==$SOCKEYE_VERSION \
    && pipenv install

COPY config/config.properties .
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh

EXPOSE 8080 8081 8443 8444

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["serve"]

LABEL version="2.1.1" \
      maintainer="james.e.woo@gmail.com" \
      source="https://github.com/jamesewoo/sockeye-serving" \
      description="A containerized service for neural machine translation"
