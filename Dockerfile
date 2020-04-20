FROM python:latest

RUN mkdir -p usr/src/dinasore-ua

WORKDIR /usr/src/dinasore-ua

COPY communication ./communication
COPY opc_ua ./opc_ua
COPY core ./core
COPY data_model ./data_model
COPY tests ./tests
COPY requirements.txt ./
COPY resources ./resources

RUN pip install -r requirements.txt

# RUN python tests/__init__.py

# ENTRYPOINT [ "python", "core/main.py" ]
