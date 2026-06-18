# Dockerfile:jeff
#
# Base build environment
#

####
FROM python:3.14-slim-trixie
LABEL maintainer="Jeffrey Carpenter <1329364+i8degrees@users.noreply.github.com>"

###

ARG VERSION=1.1.1
#USER root
#WORKDIR /
#apk add --no-cache

###

USER root
WORKDIR /
RUN set -eux \
    && dpkg --add-architecture amd64 \
    && DEBIAN_FRONTEND=noninteractive apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq -y --no-install-recommends --no-install-suggests \
    bash \
    bzip2 \
    curl \
    diffutils \
    dnsmasq \
    file \
    git \
    make \
    patch \
    python3-venv \
    unzip \
    zip \
    zstd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

###

RUN mkdir /app /app/dist
COPY .env.dist /app
#COPY .env /app/.env
COPY pyproject.toml /app
COPY requirements.txt /app
COPY config/ /app/config
COPY scripts/ /app/scripts
COPY src/ /app/src
COPY templates/ /app/templates
###

#USER app
WORKDIR /app

# expose inside container
ENV \
  PYTHONUTF8=1 \
  LC_ALL=C.UTF-8 \
  VERSION=${VERSION}

# NOTE(JEFF): Any conveniences we wish to have within the container's shell
# should be handled here if we wish for it to be permanent.
#COPY --chmod=+x --chown=root:root \
#scripts/* /scripts/
#RUN echo "INFO: Executing /build.sh..." && \
#sh -c '/app/scripts/build.sh'
RUN python3 -m pip install build # install build module
RUN python3 -m build # produce dist image
RUN python3 -m venv /app/.venv
RUN python3 -m pip install /app/dist/update_ddns_zone-${VERSION}-py3-none-any.whl
#RUN \
#chmod +x /app/scripts/docker/usage_tests.sh \
#&& /app/scripts/docker/usage_tests.sh

#python3 -m pip install --no-index --find-links=dist/ update_ddns_zone

#ENV PYTHONPATH=/app:${PYTHONPATH}

#RUN ls -lhas /
#ENTRYPOINT ["/app/.venv/bin/ddns_update", "--help"]
#ENTRYPOINT ["/app/.venv/bin/ddns_update", "-c /usr/local/etc/app.yml", "-l DEBUG", "old", "xxx", "127.0.0.1", "test" ]
