#!/bin/bash
docker stack deploy --compose-file ./docker-compose-frontend.yml --detach=false rag-frontend
