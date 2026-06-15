
REPOSITORY ?= i8degrees/ddns_update
TAG ?= dev

NPROC := $(shell nproc)
CPU_CORES ?= $(shell if [ $(NPROC) -gt 1 ]; then echo $$(($(NPROC) - 1)); else echo 1; fi)
stamp ?= date +%S

all: build-base

build-base:
	docker build \
		-t $(REPOSITORY):$(TAG) \
		--network=host \
		--push \
		--build-arg CPU_CORES=$(CPU_CORES) \
		--build-arg VERSION=1.1.1 \
		.
.PHONY: base

