set dotenv-load

dlctl := "dlctl"

# Configs
# =======

# Global
# ------

local_dir := "local/"
init_sql_path := join(local_dir, "init.sql")

engine_db_path := join(local_dir, env_var("ENGINE_DB"))

# Datasets
# --------

ds_dsn_url := "https://www.kaggle.com/datasets/andreagarritano/deezer-social-networks"
ds_msdsl_url := "https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm"
ds_dd_url := "https://huggingface.co/datasets/ShreyaR/DepressionDetection"


# Common
# ======

check-dlctl:
    which {{dlctl}} && test -x $(which {{dlctl}})

check-duckdb:
    which duckdb


# DuckLake
# ========

check-init-sql:
    test -r {{init_sql_path}} || just generate-init-sql

check-engine-db:
    test -r {{engine_db_path}}

generate-init-sql:
    {{dlctl}} tools generate-init-sql --path {{init_sql_path}}

lakehouse: check-duckdb check-init-sql check-engine-db
    duckdb -init {{init_sql_path}} {{engine_db_path}}


# GraphRAG with KùzuDB
# ====================

graphrag-etl: check-dlctl
    {{dlctl}} ingest dataset {{ds_dsn_url}}
    {{dlctl}} ingest dataset {{ds_msdsl_url}}
    {{dlctl}} transform -m "+marts.graphs.music_taste"
    {{dlctl}} export dataset graphs "music_taste"

graphrag-embeddings: check-dlctl
    {{dlctl}} graph compute embeddings "music_taste" -d 256 -b 9216 -e 5
    {{dlctl}} graph reindex "music_taste"

graphrag: check-dlctl
    {{dlctl}} graph rag "music_taste" -i

graphrag-all: graphrag-etl graphrag-embeddings graphrag


# Economic Competition Networks
# =============================

econ-compnet-ingest:
    {{dlctl}} ingest dataset -t "atlas" "The Atlas of Economic Complexity"

econ-compnet-transform:
    {{dlctl}} transform -m "+marts.graphs.econ_comp"

econ-compnet-export:
    {{dlctl}} export dataset graphs "econ_comp"

econ-compnet-load:
    {{dlctl}} graph load "econ_comp"

econ-compnet-etl: econ-compnet-ingest econ-compnet-transform econ-compnet-export econ-compnet-load

econ-compnet-scoring:
    {{dlctl}} graph compute con-score "econ_comp" "Country" "CompetesWith"

econ-compnet-all: econ-compnet-etl econ-compnet-scoring


# MLOps: A/B Testing with MLflow, Kafka, and DuckLake
# ===================================================

mlops-ingest:
    {{dlctl}} ingest dataset {{ds_dd_url}}

mlops-transform:
    {{dlctl}} transform -m "+stage.depression_detection"

mlops-etl: mlops-ingest mlops-transform

mlops-train-logreg-tfidf:
    {{dlctl}} ml train "dd" --method "logreg" --features "tfidf"

mlops-train-logreg-embeddings:
    {{dlctl}} ml train "dd" --method "logreg" --features "embeddings"

mlops-train-logreg: mlops-train-logreg-tfidf mlops-train-logreg-embeddings

mlops-train-xgboost-tfidf:
    {{dlctl}} ml train "dd" --method "xgboost" --features "tfidf"

mlops-train-xgboost-embeddings:
    {{dlctl}} ml train "dd" --method "xgboost" --features "embeddings"

mlops-train-xgboost: mlops-train-xgboost-tfidf mlops-train-xgboost-embeddings

mlops-train: mlops-train-logreg mlops-train-xgboost

mlops-serve:
    {{dlctl}} ml server

mlops-all: mlops-etl mlops-train
