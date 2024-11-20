#!/bin/bash
./wait-for-it.sh 192.168.0.101:8000
./wait-for-it.sh 192.168.0.102:11434
python rag.py
flask run --host=0.0.0.0
