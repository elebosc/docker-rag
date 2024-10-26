#!/bin/bash
ollama serve &
ollama pull llama3.2
ollama run llama3.2