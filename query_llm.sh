#!/bin/bash
curl -X POST http://localhost:8080/query -H "Content-Type: application/json" -d '{"query":"'"$1"'"}'
