#!/bin/bash
set -e

echo "Starting Ollama server in background..."
ollama serve &

echo "Waiting for Ollama to be ready..."
# Timeout in seconds
TIMEOUT=600
apt-get update && apt-get install -y curl
for i in $(seq 1 $TIMEOUT); do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/tags) || RESPONSE="N/A"
    if [ "$RESPONSE" == "200" ]; then
        echo "[$i/$TIMEOUT] Ollama is ready!"
        break
    else
        echo "[$i/$TIMEOUT] Still waiting for Ollama... Response: $RESPONSE"
    fi

    if [ $i -eq $TIMEOUT ]; then
        echo "Timeout waiting for Ollama to start after $TIMEOUT seconds"
        exit 1
    fi
    sleep 1
done
apt-get remove -y curl && apt-get autoremove -y

echo "Pulling model: ${LLM_MODEL:-codellama:7b}..."
ollama pull "${LLM_MODEL:-codellama:7b}"
echo "Model pulled successfully!"

wait
