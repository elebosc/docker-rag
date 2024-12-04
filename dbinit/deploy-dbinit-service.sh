#!/bin/bash
docker stack deploy --compose-file ./docker-compose-dbinit.yml --detach=false rag-db-init
