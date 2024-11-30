#!/bin/bash
docker stack deploy --compose-file ./docker-compose-backend.yml --detach=false rag-backend
