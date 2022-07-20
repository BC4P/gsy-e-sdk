FROM python:3.10-slim

ADD . /app

WORKDIR /app

RUN pip install -e gsy-framework -e .

ENTRYPOINT ["gsy-e-sdk run"]
