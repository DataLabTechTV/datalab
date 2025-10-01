set shell := ["bash", "-uc"]

set dotenv-load

# =======
# Configs
# =======

# ------
# Global
# ------

local_dir := "local/"
init_sql_path := join(local_dir, "init.sql")

engine_db_path := join(local_dir, env_var("ENGINE_DB"))

# --------
# Datasets
# --------

ds_dsn_url := "https://www.kaggle.com/datasets/andreagarritano/deezer-social-networks"
ds_msdsl_url := "https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm"
ds_dd_url := "https://huggingface.co/datasets/ShreyaR/DepressionDetection"
ds_dd_monitor_url := "https://huggingface.co/datasets/joangaes/depression"


# ======
# Common
# ======

default:
    just -l

check binary:
    @echo -n "Checking {{binary}}... "
    @which {{binary}} >/dev/null && test -x $(which {{binary}}) \
        || (echo "failed ({{binary}} not found)"; exit 1)
    @echo ok

check-dlctl:
    just check dlctl

check-duckdb:
    just check duckdb

check-curl:
    just check curl

check-terraform:
    just check terraform

check-docker:
    just check docker


# ========
# DuckLake
# ========

check-init-sql:
    test -r {{init_sql_path}} || just generate-init-sql

check-engine-db:
    test -r {{engine_db_path}}

generate-init-sql: check-dlctl
    dlctl tools generate-init-sql --path {{init_sql_path}}

lakehouse: check-duckdb check-init-sql check-engine-db
    duckdb -init {{init_sql_path}} {{engine_db_path}}


# ====================
# GraphRAG with KùzuDB
# ====================

graphrag-etl: check-dlctl
    dlctl ingest dataset {{ds_dsn_url}}
    dlctl ingest dataset {{ds_msdsl_url}}
    dlctl transform -m "+marts.graphs.music_taste"
    dlctl export dataset graphs "music_taste"

graphrag-embeddings: check-dlctl
    dlctl graph compute embeddings "music_taste" -d 256 -b 9216 -e 5
    dlctl graph reindex "music_taste"

graphrag: check-dlctl
    dlctl graph rag "music_taste" -i

graphrag-all: graphrag-etl graphrag-embeddings graphrag


# =============================
# Economic Competition Networks
# =============================

econ-compnet-ingest: check-dlctl
    dlctl ingest dataset -t "atlas" "The Atlas of Economic Complexity"

econ-compnet-transform: check-dlctl
    dlctl transform -m "+marts.graphs.econ_comp"

econ-compnet-export: check-dlctl
    dlctl export dataset graphs "econ_comp"

econ-compnet-load: check-dlctl
    dlctl graph load "econ_comp"

econ-compnet-etl: econ-compnet-ingest econ-compnet-transform econ-compnet-export econ-compnet-load

econ-compnet-scoring: check-dlctl
    dlctl graph compute con-score "econ_comp" "Country" "CompetesWith"

econ-compnet-all: econ-compnet-etl econ-compnet-scoring


# ===================================================
# MLOps: A/B Testing with MLflow, Kafka, and DuckLake
# ===================================================

mlops-ingest: check-dlctl
    dlctl ingest dataset {{ds_dd_url}}
    dlctl ingest dataset {{ds_dd_monitor_url}}

mlops-transform: check-dlctl
    dlctl transform -m "+stage.depression_detection"

mlops-etl: mlops-ingest mlops-transform

mlops-train-logreg-tfidf: check-dlctl
    dlctl ml train "dd" --method "logreg" --features "tfidf"

mlops-train-logreg-embeddings: check-dlctl
    dlctl ml train "dd" --method "logreg" --features "embeddings"

mlops-train-logreg: mlops-train-logreg-tfidf mlops-train-logreg-embeddings

mlops-train-xgboost-tfidf: check-dlctl
    dlctl ml train "dd" --method "xgboost" --features "tfidf"

mlops-train-xgboost-embeddings: check-dlctl
    dlctl ml train "dd" --method "xgboost" --features "embeddings"

mlops-train-xgboost: mlops-train-xgboost-tfidf mlops-train-xgboost-embeddings

mlops-train: mlops-train-logreg mlops-train-xgboost

mlops-serve: check-dlctl
    dlctl ml server

mlops_test_inference_payload := '''
{
    "models": [
        {
            "name": "dd_logreg_tfidf",
            "version": "latest"
        },
        {
            "name": "dd_xgboost_embeddings",
            "version": "latest"
        }
    ],
    "data": "hello twitter i m on a one week leave from school bc i have depression how are you all d",
    "log_to_lakehouse": true
}
'''

mlops-test-inference: check-curl
    curl -f -X POST "http://localhost:8000/inference" \
        -H "Content-Type: application/json" \
        -d '{{mlops_test_inference_payload}}'
    @echo
    curl -f -X GET "http://localhost:8000/inference/logs/flush"

mlops-test-feedback uuid feedback: check-curl
    curl -f -X PATCH "http://localhost:8000/inference" \
        -H "Content-Type: application/json" \
        -d '{"inference_uuid": "{{uuid}}", "feedback": {{feedback}}}'
    curl -f -X GET "http://localhost:8000/inference/logs/flush"

mlops-simulate-inference: check-dlctl
    dlctl ml simulate "dd" \
        --sample-fraction 0.01 \
        --model-uri "models:/dd_xgboost_embeddings/latest" \
        --model-uri "models:/dd_logreg_tfidf/latest"

mlops-monitor-compute: check-dlctl
    dlctl ml monitor compute "dd" \
        --model-uri "models:/dd_xgboost_embeddings/latest" \
        --model-uri "models:/dd_logreg_tfidf/latest"

mlops-monitor-plot: check-dlctl
    dlctl ml monitor plot "dd" \
        --model-uri "models:/dd_xgboost_embeddings/latest" \
        --model-uri "models:/dd_logreg_tfidf/latest"

mlops-all: mlops-etl mlops-train


# ==============
# Data Lab Infra
# ==============

docker_shared_context := "docker-shared"

# -------------
# Config Checks
# -------------

infra-config-check-foundation: check-terraform
    @echo -n "Checking foundation configs... "
    @test -f infra/foundation/terraform.tfvars \
        || (echo "failed (terraform.tfvars: not found)"; exit 1)
    @echo ok

infra-config-check-platform: check-terraform
    @echo -n "Checking platform configs... "
    @test -f infra/platform/terraform.tfvars \
        || (echo "failed: terraform.tfvars not found"; exit 1)
    @test -f infra/platform/state.config \
        || (echo "state.config: not found"; exit 2)
    @echo ok

infra-config-check-services: check-docker
    @echo -n "Checking {{docker_shared_context}} docker context... "
    @docker context ls --format "{{{{.Name}}" | grep -q '^{{docker_shared_context}}$' \
        || (echo "failed: {{docker_shared_context}} docker context not configured"; exit 1)
    @echo ok

infra-config-check-all: infra-config-check-foundation \
    infra-config-check-platform \
    infra-config-check-services

# ---------------
# Initializations
# ---------------

infra-foundation-init: infra-config-check-foundation
    terraform -chdir=infra/foundation init

infra-platform-init: infra-config-check-platform
    terraform -chdir=infra/platform init -backend-config=state.config

infra-init: infra-foundation-init infra-platform-init

# ------------
# Provisioning
# ------------

infra-provision-foundation: infra-config-check-foundation
    terraform -chdir=infra/foundation apply

infra-provision-platform: infra-config-check-platform
    terraform -chdir=infra/platform apply

infra-provision-services: infra-config-check-services
    docker -c {{docker_shared_context}} compose -p datalab -f infra/services/compose.yml up -d

infra-provision-all: infra-provision-foundation \
    infra-provision-platform \
    infra-provision-services

infra-provision-local:
    docker compose -p datalab -f infra/services/compose.yml --profile dev up -d

# -----------
# Destruction
# -----------

infra-destroy-foundation:
    terraform -chdir=infra/foundation destroy

infra-destroy-platform:
    terraform -chdir=infra/platform destroy

infra-destroy-services:
    docker -c {{docker_shared_context}} compose -p datalab -f infra/services/compose.yml down -v

infra-destroy-all: infra-destroy-services \
    infra-destroy-platform \
    infra-destroy-foundation

infra-destroy-local:
    docker compose -p datalab -f infra/services/compose.yml --profile dev down -v

# ---------
# Utilities
# ---------

infra-show-tf-credentials layer:
    @[[ " foundation platform " == *" {{layer}} "* ]] \
        || (echo "{{layer}}: invalid layer"; exit 1)
    @terraform -chdir=infra/{{layer}} output -json \
        | jq -r 'to_entries[] \
        | select(.value.sensitive==true) \
        | "\(.key) = \(.value.value)"'

infra-show-credentials: infra-config-check-all
    @echo
    @echo "=========="
    @echo "Foundation"
    @echo "=========="
    @just infra-show-tf-credentials foundation
    @echo
    @echo "========"
    @echo "Platform"
    @echo "========"
    @just infra-show-tf-credentials platform
