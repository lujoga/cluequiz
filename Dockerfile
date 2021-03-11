FROM debian:bullseye-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV CONFIG_FILE=config.example.yml
ENV DEBUG=no
ENV VIEWER=no

RUN apt-get update && apt-get -y --no-install-recommends install \
	fontconfig \
	fonts-dejavu \
	python3 \
	python3-paho-mqtt \
	python3-pil \
	python3-pip \
	python3-pygame \
	python3-pygments \
	python3-serial \
	python3-yaml

COPY cluequiz /usr/local/src/cluequiz/cluequiz/
COPY LICENSE README.md setup.py /usr/local/src/cluequiz/
COPY clue-set.example.yml config.example.yml /opt/cluequiz/

RUN cd /usr/local/src/cluequiz && pip3 install .

WORKDIR /opt/cluequiz

CMD ["cluequiz"]
