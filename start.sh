export APP_EMBEDDINGS_SERVERURL=""
export APP_LLM_SERVERURL=""
export APP_RANKING_SERVERURL=""
export EMBEDDING_NIM_ENDPOINT="https://integrate.api.nvidia.com/v1"
export PADDLE_HTTP_ENDPOINT="https://ai.api.nvidia.com/v1/cv/baidu/paddleocr"
export PADDLE_INFER_PROTOCOL="http"
export YOLOX_HTTP_ENDPOINT="https://ai.api.nvidia.com/v1/cv/nvidia/nemoretriever-page-elements-v2"
export YOLOX_INFER_PROTOCOL="http"
export YOLOX_GRAPHIC_ELEMENTS_HTTP_ENDPOINT="https://ai.api.nvidia.com/v1/cv/nvidia/nemoretriever-graphic-elements-v1"
export YOLOX_GRAPHIC_ELEMENTS_INFER_PROTOCOL="http"
export YOLOX_TABLE_STRUCTURE_HTTP_ENDPOINT="https://ai.api.nvidia.com/v1/cv/nvidia/nemoretriever-table-structure-v1"
export YOLOX_TABLE_STRUCTURE_INFER_PROTOCOL="http"

docker compose -f deploy/compose/vectordb.yaml down 
docker compose -f deploy/compose/docker-compose-ingestor-server.yaml down
docker compose -f deploy/compose/docker-compose-rag-server.yaml down


docker compose -f deploy/compose/vectordb.yaml up -d --build
docker compose -f deploy/compose/docker-compose-ingestor-server.yaml up -d --build
docker compose -f deploy/compose/docker-compose-rag-server.yaml up -d --build


# Health check
# curl -X 'GET' '127.0.0.1:8081/v1/health?check_dependencies=true' -H 'accept: application/json'

docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"