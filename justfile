set dotenv-load

dlctl := "dlctl"

# Configs
# =======

# Global
# ------

local_dir := "local/"
init_sql_path := local_dir + "/init.sql"

# Datasets
# --------

ds_dsn_url := "https://www.kaggle.com/datasets/andreagarritano/deezer-social-networks"
ds_msdsl_url := "https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm"
ds_depression_detection_url := "https://huggingface.co/datasets/ShreyaR/DepressionDetection"


# Common
# ======

check-dlctl:
    which {{dlctl}} && test -x $(which {{dlctl}})

check-duckdb:
    which duckdb


# DuckLake
# ========

check-init-sql:
    test -r {{init_sql_path}}

check-engine-db:
    test -r {{local_dir}}/${ENGINE_DB}

lakehouse: check-duckdb check-init-sql check-engine-db
    duckdb -init {{init_sql_path}} {{local_dir}}/${ENGINE_DB}


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

econ-compnet-etl:
    {{dlctl}} ingest dataset -t "atlas" "The Atlas of Economic Complexity"
    {{dlctl}} transform -m "+marts.graphs.econ_comp"
    {{dlctl}} export dataset graphs "econ_comp"
    {{dlctl}} graph load "econ_comp"

econ-compnet-scoring:
    {{dlctl}} graph compute con-score "econ_comp" "Country" "CompetesWith"

econ-compnet-all: econ-compnet-etl econ-compnet-scoring


# Operational A/B Testing with MLflow and DuckLake
# ================================================

ml-ab-testing-etl:
    {{dlctl}} ingest dataset {{ds_depression_detection_url}}
    {{dlctl}} transform -m "+stage.depression_detection"

ml-ab-testing-train-logreg:
    {{dlctl}} ml train "depression_detection" \
        --text "clean_text" \
        --label "is_depression" \
        --method "logreg"

ml-ab-testing-train-xgboost:
    {{dlctl}} ml train "depression_detection" \
        --text "clean_text" \
        --label "is_depression" \
        --method "xgboost"

ml-ab-testing-train: ml-ab-testing-train-logreg ml-ab-testing-train-xgboost

ml-ab-testing-test-logreg:
    {{dlctl}} ml test "depression_detection" --method "logreg"

ml-ab-testing-test-xgboost:
    {{dlctl}} ml test "depression_detection" --method "xgboost"

ml-ab-testing-test: ml-ab-testing-test-logreg ml-ab-testing-test-xgboost

ml-ab-testing-all: ml-ab-testing-etl ml-ab-testing-train ml-ab-testing-test
