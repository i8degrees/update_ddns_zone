# Dockerfile:jeff
#
# Base build environment
#

FROM python:3.14:alpine
LABEL maintainer="Jeffrey Carpenter <1329364+i8degrees@users.noreply.github.com>"

USER root
WORKDIR /
#apk add --no-cache

# NOTE(JEFF): Any conveniences we wish to have within the container's shell
# should be handled here if we wish for it to be permanent.
COPY . /app/
#COPY --chmod=+x --chown=root:root \
#scripts/* /scripts/
RUN echo "INFO: Executing /build.sh..." && \
  sh -c '/app/scripts/build.sh'

USER app
WORKDIR /app
ENTRYPOINT ["ddns_update", "--help" ]

