FROM python:3.6

RUN mkdir -p usr/src/dinasore-ua

WORKDIR /usr/src/dinasore-ua

ADD communication ./communication
ADD opc_ua ./opc_ua
ADD core ./core
ADD data_model ./data_model
ADD tests ./tests
ADD requirements.txt ./

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "core/main.py" ]
