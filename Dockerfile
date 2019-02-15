FROM python:3.6

RUN mkdir -p usr/src/dinasore

WORKDIR /usr/src/dinasore

ADD communication ./communication
ADD core ./core
ADD resources ./resources
ADD tests ./tests

ENTRYPOINT [ "python" ]