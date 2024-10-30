#!/bin/bash
ollama serve &
ollama create mistralgguf -f ./models/Modelfile
ollama run mistralgguf
