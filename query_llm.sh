#!/bin/bash
curl -X POST http://127.0.0.1:8080/query -H "Content-Type: application/json" -d '{"query":"'"$1"'"}'
