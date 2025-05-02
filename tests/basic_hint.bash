#!/bin/bash

# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# Exit immediately on error
set -e

# Endpoint
ENDPOINT="http://localhost:8081/generate_hint"

# Path to hint elements file
HINT_ELEMENTS_FILE="tests/light_hint_element_example.json"

# Check if file exists
if [[ ! -f "$HINT_ELEMENTS_FILE" ]]; then
  echo "Error: File $HINT_ELEMENTS_FILE does not exist."
  exit 1
fi

# Compose the full payload
echo "Sending request to $ENDPOINT using $HINT_ELEMENTS_FILE..."

PAYLOAD=$(jq -n \
  --argjson hint_elements "$(cat $HINT_ELEMENTS_FILE)" \
  --arg model "your-model-name" \
  --arg collection_name "your-collection-name" \
  '{
    hint_elements: $hint_elements,
    use_knowledge_base: false,
    temperature: 0.2,
    top_p: 0.7,
    max_tokens: 100,
    top_k: 4,
    stop: []
  }')

# Send the request
curl -X POST "$ENDPOINT" \
     -H "Content-Type: application/json" \
     --data "$PAYLOAD" \

echo -e "\nRequest complete."
