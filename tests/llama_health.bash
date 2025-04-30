#!/bin/bash

CONTAINER_NAME="llama-light"
PORT=8088
TEST_PROMPT="Explain quantum computing in simple terms."

# Step 1: Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Container '${CONTAINER_NAME}' is not running."
    exit 1
fi
echo "✅ Container '${CONTAINER_NAME}' is running."

# Step 2: Check /health endpoint
echo -n "🔍 Checking health endpoint... "
if curl -sf "http://localhost:${PORT}/health" >/dev/null; then
    echo "Healthy ✅"
else
    echo "Unhealthy ❌"
    exit 1
fi

# Step 3: Send a test prompt
echo "💬 Sending test prompt to LLM..."

RESPONSE=$(curl -s -X POST "http://localhost:${PORT}/generate" \
    -H "Content-Type: application/json" \
    -d '{
        "inputs": "<|user|>\nExplain quantum computing in simple terms.\n<|assistant|>",
        "parameters": {
            "max_new_tokens": 50,
            "do_sample": true,
            "temperature": 0.7
        }
    }')


# Step 4: Check response
if echo "$RESPONSE" | grep -q "generated_text"; then
    echo "✅ LLM response received:"
    echo "$RESPONSE" | jq
else
    echo "❌ LLM did not respond properly:"
    echo "$RESPONSE"
    exit 1
fi
