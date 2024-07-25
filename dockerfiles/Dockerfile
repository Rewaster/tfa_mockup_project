FROM python:3.10-slim

RUN apt-get update  \
    && apt-get install -y \
        curl \
        wget \
        nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY .. .
RUN pip3 install -r /usr/src/app/requirements.txt

ENV PYTHONPATH /usr/src/app
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENTRYPOINT ["sh", "scripts/entrypoint.sh"]
