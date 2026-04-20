# Dockerfile:jeff
#
# Base build environment
#

FROM python:3.14-slim-trixie
LABEL maintainer="Jeffrey Carpenter <1329364+i8degrees@users.noreply.github.com>"

#USER root
#WORKDIR /
#apk add --no-cache

USER root
WORKDIR /
RUN apt-get update -y && apt-get install dnsmasq -y
RUN mkdir /app
COPY . /app/
#USER root
WORKDIR /app

# NOTE(JEFF): Any conveniences we wish to have within the container's shell
# should be handled here if we wish for it to be permanent.
#COPY --chmod=+x --chown=root:root \
#scripts/* /scripts/
#RUN echo "INFO: Executing /build.sh..." && \
#sh -c '/app/scripts/build.sh'
RUN python3 -m pip install build
RUN python3 -m build

ENV PYTHONPATH=/app:${PYTHONPATH}

ENTRYPOINT ["ddns_update", "--help" ]

