FROM ubuntu:20.04 AS builder

LABEL maintainer="Navan Chauhan <navanchauhan@gmail.com>" \
        org.label-schema.name="Curie Module" \
        org.label-schema.description="https://navanchauhan.github.io/Curie"

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
    git \
    libopenbabel-dev \
    libopenbabel6 \
    pymol \
    python3-distutils \
    python3-lxml \
    python3-openbabel \
    python3-pymol \
    python3-pip \
    openbabel \
    autodock-vina \
    pandoc \
    texlive-xetex \
    imagemagick \
    python3-rdkit \
    libmysqlclient-dev \
    mysql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 8080

WORKDIR /curie-web

COPY requirements-docker.txt /curie-web
RUN python3 -m pip install -r requirements-docker.txt

# Install PLIP
RUN git clone https://github.com/navanchauhan/plip source \
    && cd source \
    && python3 setup.py install \
    && cd .. \
    && rm -r source

COPY config.ini /curie-web
COPY app /curie-web/app

COPY run.py /curie-web
COPY api.py /curie-web

COPY lstm_chem /curie-web/lstm_chem

CMD gunicorn -w 4 api:app -k uvicorn.workers.UvicornWorker -b "0.0.0.0:8080"
