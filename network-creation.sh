#!/bin/bash
docker network create --driver overlay --internal --scope=swarm --attachable rag-backend-net
docker network create --driver bridge --scope=swarm --attachable rag-frontend-net
