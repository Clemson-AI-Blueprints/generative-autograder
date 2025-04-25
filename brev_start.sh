#!/usr/bin/env bash
set -e

# 👇 Load .env variables into the current shell
set -o allexport
source .env
set +o allexport

echo "$NVIDIA_API_KEY" | docker login nvcr.io -u '$oauthtoken' --password-stdin
# echo "$GITHUB_PAT" | docker login ghcr.io -u your-github-username --password-stdin

docker compose -f deploy/compose/docker-compose-brev.yaml down
docker compose -f deploy/compose/docker-compose-brev.yaml up -d --build