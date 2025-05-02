
echo "Running Llama with within context..."
curl -s -X POST "http://localhost:8088/generate" \
    -H "Content-Type: application/json" \
    -d '{
        "inputs": "<|user|>\nExplain quantum computing in simple terms.\n<|assistant|>",
        "parameters": {
            "max_new_tokens": 50,
            "do_sample": true,
            "temperature": 0.7
        }
    }'

echo "Running Llama with within context on llama-light..."

curl -s -X POST "http://llama-light:80/generate" \
    -H "Content-Type: application/json" \
    -d '{
        "inputs": "<|user|>\nExplain french computing in simple terms.\n<|assistant|>",
        "parameters": {
            "max_new_tokens": 50,
            "do_sample": true,
            "temperature": 0.7
        }
    }'