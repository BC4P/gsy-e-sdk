FROM python:3.10-slim

ADD . /app

WORKDIR /app

RUN pip install -e .

ENTRYPOINT ["python"]
