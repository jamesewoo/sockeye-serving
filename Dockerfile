FROM nvidia/cuda:9.2-cudnn7-runtime-centos7

ENV PYTHONUNBUFFERED TRUE

RUN useradd -m model-server && \
    mkdir -p /home/model-server/tmp

WORKDIR /home/model-server
ENV TEMP=/home/model-server/tmp

RUN yum install -y python36-devel gcc java-1.8.0-openjdk-devel
RUN python --version && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.6 100 && \
    python --version

COPY requirements/ requirements/
RUN python -m venv venv && \
    source venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install sockeye --no-deps -r requirements/sockeye/requirements.gpu-cu92.txt && \
    pip install --no-cache-dir mxnet-model-server
RUN pip install -r requirements/sockeye-serving/requirements.txt

COPY scripts/mms/dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh
COPY config/mms/config.properties /home/model-server
COPY config/sockeye/args.txt ./
COPY data/ src/ ./

RUN chmod +x /usr/local/bin/dockerd-entrypoint.sh && \
    chown -R model-server /home/model-server

EXPOSE 8080 8081

USER model-server
ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
CMD ["serve"]

LABEL maintainer="james.e.woo@gmail.com"
