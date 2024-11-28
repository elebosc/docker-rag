#!/bin/bash
# ./wait-for-it.sh rag-backend_chroma:8000
# ./wait-for-it.sh rag-backend_ollama:11434
python rag.py
flask run --host=0.0.0.0
