#!/bin/sh

echo "Pulling Ollama model: $PULL"
docker exec datalab-ollama-1 ollama pull "$PULL"
