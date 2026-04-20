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
RUN apt-get update && apt-get install dnsmasq python3-venv git -y

#
RUN mkdir /app /app/dist
COPY .env.dist /app
#COPY .env /app/.env
COPY pyproject.toml /app
COPY requirements.txt /app
COPY config/ /app/config
COPY scripts/ /app/scripts
COPY src/ /app/src
COPY templates/ /app/templates
#USER app
WORKDIR /app

# NOTE(JEFF): Any conveniences we wish to have within the container's shell
# should be handled here if we wish for it to be permanent.
#COPY --chmod=+x --chown=root:root \
#scripts/* /scripts/
#RUN echo "INFO: Executing /build.sh..." && \
#sh -c '/app/scripts/build.sh'
RUN python3 -m pip install build # install build module
RUN python3 -m build # produce dist image
RUN python3 -m venv /app/.venv
RUN python3 -m pip install /app/dist/update_ddns_zone-1.0.0-py3-none-any.whl
#python3 -m pip install --no-index --find-links=dist/ update_ddns_zone

#ENV PYTHONPATH=/app:${PYTHONPATH}

#RUN ls -lhas /
#ENTRYPOINT ["/app/.venv/bin/ddns_update", "--help"]
#ENTRYPOINT ["/app/.venv/bin/ddns_update", "-c /usr/local/etc/app.yml", "-l DEBUG", "old", "xxx", "127.0.0.1", "test" ]
