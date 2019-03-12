FROM nvidia/cuda:9.2-cudnn7-runtime-ubuntu18.04

ENV TEMP=/home/model-server/tmp
ENV SOCKEYE_VERSION=1.18.78
ENV PYTHONUNBUFFERED TRUE

RUN useradd -m model-server && \
    mkdir -p $TEMP && \
    chown model-server $TEMP

WORKDIR /home/model-server

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    python3-dev \
    python3-venv \
    openjdk-8-jdk-headless \
    curl \
    vim && \
    rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir sockeye==$SOCKEYE_VERSION \
        --no-deps -r requirements/sockeye/requirements.gpu-cu92.txt && \
    pip install --no-cache-dir -r requirements/sockeye-serving/requirements.txt

COPY config/config.properties .
COPY scripts/mms/dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh

EXPOSE 8080 8081

USER model-server
ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
CMD ["serve"]

LABEL version="1.0.0" \
      maintainer="james.e.woo@gmail.com" \
      source="https://github.com/jamesewoo/sockeye-serving" \
      description="Sockeye server based on mxnet-model-server"
