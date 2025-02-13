#!/bin/bash
docker network create --driver overlay --internal --scope=swarm rag-overlay-internal-net
docker network create --driver bridge --scope=swarm rag-bridge-net
