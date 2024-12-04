#!/bin/bash
# $1 --> container name
docker logs --tail 50 --follow --timestamps $1
