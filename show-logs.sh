#!/bin/bash
# $1 --> number of lines to show
# $2 --> container name
docker logs --tail $1 --follow --timestamps $2
