FROM python:3.6

RUN mkdir -p usr/src/dinasore

WORKDIR /usr/src/dinasore

ADD communication ./communication
ADD core ./core
ADD resources ./resources
ADD tests ./tests

RUN python tests/__init__.py

ENTRYPOINT [ "python", "core/main.py" ]