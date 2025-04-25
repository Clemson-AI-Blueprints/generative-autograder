<h1><img align="center" src="https://github.com/Clemson-AI-Blueprints/generative-autograder/blob/ecc4ef8290ec5b90878ad6800e0331f912142b0f/assets/icon.png">Generative Autograder Blueprint</h1>

Use this documentation to understand, deploy, and customize the **Generative Autograder Hint Server**—a Retrieval‑Augmented Generation (RAG) service that produces pedagogically‑sound hints for programming assignments.

- [Overview](#overview)
- [Key Features](#key-features)
- [Target Audience](#target-audience)
- [Software Components](#software-components)
- [Technical Diagram](#technical-diagram)
- [Minimum System Requirements](#minimum-system-requirements)
  - [OS Requirements](#os-requirements)
  - [Deployment Options](#deployment-options)
  - [Driver Versions](#driver-versions)
  - [Hardware Requirements](#hardware-requirements)
- [Next Steps](#next-steps)
- [Available Customizations](#available-customizations)
- [Contributing](#contributing)
- [License](#license)

---
## Overview
This repository repurposes the NVIDIA RAG Blueprint to power an **autograder‑aware hint generator** for introductory Computer Science courses (CPSC 10xx).  
During grading, the complementary autograder framework ([cu‑autograder‑framework](https://github.com/Elan456/cu-autograder-framework)) sends a *hint generation request* to this server that contains:

1. **Failure elements** – compiler/runtime errors, failed test output, static‑analysis feedback
2. **Assignment context** – project id
3. **Student code** – the source file(s) that triggered the failure

The RAG pipeline grounds an LLM with the reference material and returns a concise, actionable hint that helps the student iterate without giving the full solution away.

The server also exposes a `/config` UI where course staff upload project directions, sample code, and reference output.  These documents are automatically chunked, embedded, and indexed for retrieval.

---
## Key Features
- **LLM‑Powered Hints** – Generates one‐to‐three short suggestions rather than verbose explanations.
- **Course‑Aware RAG** – Retrieves only instructor‑approved context scoped to the current assignment.
- **Pluggable Autograder** – Drop‑in REST endpoint for any grading workflow; first‑class support for the [CU-autograder-framework](https://github.com/Elan456/cu-autograder-framework).
- **Self‑Hosted or Cloud** – Runs locally on a single NVIDIA T4 or connects to NVIDIA‑hosted NIMs.
- **/config Admin Portal** – Web form to ingest directions, starter files, and sample output.
- **Telemetry Ready** – Optional Redis & OTEL hooks for usage analytics.

---
## Target Audience
* **Autograder Developers** who want to augment automated assessment with formative feedback.
* **Instructors & TAs** for large‑enrollment intro programming courses seeking scalable, consistent hints.

---
## Software Components
The default Docker Compose stack (see [`docker-compose-brev.yaml`](./deploy/compose/docker-compose-brev.yaml)) launches:

| Service | Image | Purpose |
|---------|-------|---------|
| **rag-server** | `nvcr.io/nvidia/blueprint/rag-server` | Orchestrates the hint pipeline (retrieval → ranking → generation). |
| **ingestor-server** | `nvcr.io/nvidia/blueprint/ingestor-server` | Ingests `/config` documents into Milvus. |
| **milvus** + **minio** + **etcd** | GPU‑accelerated vector DB & object store. |
| **llama-8b-light** | `ghcr.io/huggingface/text-generation-inference` | 8 B parameter GPT‑Q LLM for hint generation. |
| **bge-embedding-ms** | `ghcr.io/huggingface/text-embeddings-inference` | Sentence embeddings for retrieval. |
| **mini‑reranker‑ms** | `ghcr.io/huggingface/text-generation-inference` | Reranks retrieved chunks for precision. |
| **redis (optional)** | `redis/redis-stack` | Message bus & caching for high‑traffic deployments. |

> **Ports**:  
> `rag-server` → `8081`  |  hint generation endpoint: `POST /generate_hint` on `8081`.

---
## Technical Diagram
_Coming soon_ – The flow mirrors the NVIDIA RAG diagram with the autograder replacing the playground UI and a `/config` ingestion path.

---
## Minimum System Requirements
### OS Requirements
Ubuntu 22.04 LTS

### Deployment Options
- **Docker Compose** (single GPU) – recommended for classroom & CI use.

### Driver Versions
- NVIDIA Driver ≥ 535.xx  
- CUDA 12.6+  
- Docker 24+

### Hardware Requirements
| Scenario | Minimum GPU | vRAM | Notes |
|----------|-------------|------|-------|
| Self‑host all services | **1× T4** | 16 GB | Verified in production at Clemson SoC autograder. |
| External LLM via NVIDIA API | CPU‑only | — | Set `APP_LLM_SERVERURL` to hosted NIM. |

For heavy concurrent load (>300 simultaneous submissions) provision a second GPU for Milvus indexing.

---
## Next Steps
1. **Clone** the repo and copy `.env.example` → `.env`, filling in `NVIDIA_API_KEY` and optional `HUGGING_FACE_HUB_TOKEN`.
2. **Ingest assignment material** via `/config` or by `curl -X POST /documents` with your PDFs / code.
3. **Launch** `bash brev_start.sh` to start the stack.  This will take a few minutes to download the images and start the services. It will load all the environment variables from `.env` and start the services in the background.
   - **Note**: If you are using a different GPU, edit `docker-compose-brev.yaml` to set the correct GPU.
   - **Note**: If you are using a different NVIDIA NIM, edit `docker-compose-brev.yaml` to set the correct NIM.
4. **Call** `POST http://localhost:8081/generate` with a JSON payload matching the [OpenAPI spec](./docs/api/openapi.yaml).

---
## Available Customizations
- **Swap Models** – Edit env vars in `docker-compose-brev.yaml` to use larger or hosted NIMs.

---
## Contributing
Issues and PRs welcome!  Read our [contributing guidelines](./CONTRIBUTING.md) and join us in building better automated tutoring tools.

---
## License
Released under the [Apache 2.0 License](./LICENSE).  See [`LICENSE-3rd-party.txt`](./LICENSE-3rd-party.txt) for third‑party notices.  NVIDIA NIM usage governed by the NVIDIA Software License Agreement and associated model licenses.

