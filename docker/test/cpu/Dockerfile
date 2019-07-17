FROM jwoo11/sockeye-serving:2.1.0-devel

USER root
WORKDIR /home/serving

COPY test.sh .

ENTRYPOINT ["./test.sh"]
CMD ["test"]

LABEL version="2.1.0" \
      maintainer="james.e.woo@gmail.com" \
      source="https://github.com/jamesewoo/sockeye-serving" \
      description="A containerized service for neural machine translation"
