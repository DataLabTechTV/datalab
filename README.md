# 🧪 Data Lab

Tooling for a minimalist data lab running on top of DuckLake.

## 📋 Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) with [Python 3.13](https://docs.astral.sh/uv/guides/install-python/#installing-a-specific-version) installed.
- Access to [MinIO](https://min.io/) or [S3](https://aws.amazon.com/s3/)-compatible object storage.

I keep a MinIO instance on my tiny home lab, made of an old laptop running Proxmox, but you can easily spin up a MinIO instance using the `docker-compose.yml` that we provide (after setting up your `.env`, see below).

> [!NOTE] dbt-duckdb
> We rely on the official [duckdb/dbt-duckdb](https://github.com/duckdb/dbt-duckdb) adapter to connect to DuckLake. At this time, the latest stable version of the adapter does not support attaching the external DuckLake catalog with the `DATA_PATH` option and S3 credentials, but there is [PR #564](https://github.com/duckdb/dbt-duckdb/issues/564) that solves this, so we're using what is, at this point, unreleased code (see the [dbt-duckdb](pyproject.toml#L16) dependency and the corresponding entry under [[tools.uv.sources]](pyproject.toml#L37) in the [pyproject.toml](pyproject.toml) file).

## 🚀 Quick Start

First create your own `.env` file from the provided example:

```bash
cp .env.example .env
```

Make sure you fill-in the S3 configuration for:

```bash
S3_ACCESS_KEY_ID=minio_username
S3_SECRET_ACCESS_KEY=minio_password
```

You can then setup the MinIO service as follows (it will use your env vars):

```bash
docker compose up -d
```

If you're you're having trouble connecting to MinIO, make sure you're using the correct zone, which you set via the `S3_REGION` variable in `.env`. You might need to go into http://localhost:9001 to setup your default region under Configuration → Region.

You can then install `dlctl` via:

```bash
uv sync
source .venv/bin/activate
```

You should also generate the `init.sql` file, so you can easily connect to your DuckLake from the CLI as well:

```bash
dlctl tools generate-init-sql
duckdb -init local/init.sql local/engine.duckdb
```

The general workflow you're expected to follow is illustrated in the following diagram:

![Data Lab Architecture Diagram](docs/datalab-architecture.png)

You're expected to implement your own [dbt](https://docs.getdbt.com/) models to power `dlctl transform`. We provide an example of this under `transform/models/`, based on the following Kaggle datasets:

- [andreagarritano/deezer-social-networks](https://www.kaggle.com/datasets/andreagarritano/deezer-social-networks)
- [undefinenull/million-song-dataset-spotify-lastfm](https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm)

You can learn all other details below.

## 🧩 Components

### dlctl/

This is where the `dlctl` command lives—standing for 'Data Lab Control'. This helps you run all the tasks supported by the data lab package. It is available as a script under [pyproject.toml](pyproject.toml#L31) and it can be accessed via:

```bash
uv sync
source .venv/bin/activate
dlctl ...
```

> [!NOTE] Unindexed Dependencies
> A few `torch` dependencies, like `torch_sparse` require `UV_FIND_LINKS` to be set when adding or removing any dependencies, but not during install, where `uv.lock` already has all the required information. We currently don't rely on this, but, if we do in the future, here's how to approach it:
>
> ```bash
> export UV_FIND_LINKS="https://data.pyg.org/whl/torch-2.7.0+cu126.html"
> uv add --no-build-isolation pyg_lib torch_scatter torch_sparse \
>   torch_cluster torch_spline_conv
> ```

### ingest/

Helps manage ingestion from difference data sources, creating the proper directory structure (see [Storage Layout](#%EF%B8%8F-storage-layout)) consisting of the retrieval for raw data and the creation proper directory structure creation. Raw data might be dropped manually, from Kaggle, Hugging Face, or some other source. This will make it easy to load it and keep it organized.

### transform/

This is the core of the data lakehouse, using [dbt](https://docs.getdbt.com/) to transform raw data into usable data, with [DuckLake](https://ducklake.select/) as the underlying catalog, running on top of SQLite.

We purposely keep this simple with SQLite, using a backup/restore strategy to/from S3, as this assumes exploratory lab work, but you can easily replace [SQLite](https://ducklake.select/docs/stable/duckdb/usage/choosing_a_catalog_database#sqlite) with a [PostgreSQL](https://ducklake.select/docs/stable/duckdb/usage/choosing_a_catalog_database#postgresql) node, if you prefer.

### export/

Gold tier datasets under your data marts are only usable externally after you export them. This component manages exports, creating them for a specific data mart catalog and schema, listing them, or purging old versions.

### graph/

Graph loading and computation on top of KùzuDB. We support operations like graph loading from S3 parquet files, and node embedding via FRP (Fast Random Projection), which is implemented using node batching with input/output from/to KùzuDB and training on top of PyTorch.

### shared/

Includes five modules:

- `settings`, which loads and provides access to environment variables and other relevant constants;
- `storage`, which handles mid-level S3 storage operations, like creating a dated directory structure, uploading and downloading files and directories, or managing the manifest files;
- `lakehouse`, which connects the DuckDB engine and helps with tasks like exporting datasets, or loading the latest snapshot for an export;
- `templates` contains helper functions and `string.Template` instances to produce files like `init.sql`;
- `tools` provides a function per CLI tool (callable via `dlctl tools`), for example to generate the `init.sql` file described in the `templates` module.

### scripts/

Individual Bash or Python scripts for generic tasks (e.g., launching KùzuDB Explorer).

### local/

Untracked directory where all your local files will live. This includes the engine database (DuckDB) and the DuckLake catalogs (e.g., `stage.sqlite`, `marts/graphs.sqlite`), which you can restore from a [backup](#backup), or create from scratch. KùzuDB databases will also live here, under `graphs/`, as well as the `init.sql` script for CLI access to the lakehouse.


## 🗃️ Storage Layout

All data is stored in a single S3 bucket (e.g., `s3://lakehouse`, tested with MinIO), with directory structure:

```
s3://lakehouse/
├── backups/
│   └── catalog/
│       ├── YYYY_MM_DD/
│       │   └── HH_mm_SS_sss/
│       │       ├── engine.duckdb
│       │       ├── stage.sqlite
│       │       └── marts/*.sqlite
│       └── manifest.json
├── raw/
│   └── <dataset-name>/
│       ├── YYYY_MM_DD/
│       │   └── HH_mm_SS_sss/
│       │       ├── *.csv
│       │       ├── *.json
│       │       └── *.parquet
│       └── manifest.json
├── stage/
│   └── ducklake-*.parquet
├── marts/
│   └── <domain>/
│           └── ducklake-*.parquet
└── exports/
    └── <domain>/
        └── <dataset-name>/
            ├── YYYY_MM_DD/
            │   └── HH_mm_SS_sss/
            │       ├── *.csv
            │       ├── *.json
            │       └── *.parquet
            └── manifest.json
```

> [!NOTE]
> Date/time entries should be always UTC.

## ⚙️ Configuration

Configuration for data lab is all done through the environment variables defined in `.env`.

This will also support the generation of an `init.sql` file, which contains the DuckLake configurations, including the MinIO/S3 secret and all attached catalogs.

### Environment Variables

#### S3 Configurations

```bash
S3_ENDPOINT=localhost:9000
S3_USE_SSL=false
S3_URL_STYLE=path
S3_ACCESS_KEY_ID=minio_username
S3_SECRET_ACCESS_KEY=minio_password
S3_REGION=eu-west-1
```

`S3_ENDPOINT` and `S3_URL_STYLE` are only required if you're using a non-AWS object store like MinIO.

`S3_REGION` must match MinIO's region (explicitly setting one in MinIO is recommended).


#### Data Lab Specifics

```bash
S3_BUCKET=lakehouse
S3_INGEST_PREFIX=raw
S3_STAGE_PREFIX=stage
S3_GRAPHS_MART_PREFIX=marts/graphs
S3_EXPORTS_PREFIX=exports
S3_BACKUPS_PREFIX=backups
```

You can use the defaults here. Everything will live under the `S3_BUCKET`. Each stage has its own prefix under that bucket, but the mart prefixes are special—any environment variable that ends with `*_MART_PREFIX` will be associated with its down `*_MART_DB`, as show in the next section.

#### DuckLake Configurations

```bash
ENGINE_DB=engine.duckdb
STAGE_DB=stage.sqlite
GRAPHS_MART_DB=marts/graphs.sqlite
```

These files will live under `local/`. The DuckDB `ENGINE_DB` will be leveraged for querying. All data is tracked on the `STAGE_DB` and `*_MART_DB` catalog databases and stored on the corresponding object storage locations, as shown in the previous section.

### KùzuDB Configurations

```bash
MUSIC_TASTE_GRAPH_DB=graphs/music_taste
```

The data lab also leverages [KùzuDB](https://kuzudb.com/) for graph data science tasks. The path for each graph database can be set here as `*_GRAPH_DB`.

### Generating init.sql

You can generate an `init.sql` once you setup your `.env`, so you can access your DuckLake from the CLI using `duckdb`:

```bash
dlctl tools generate-init-sql
duckdb -init local/init.sql local/engine.duckdb
```

## 📖 Usage

### Ingestion

As a rule of thumb, ingestion will be done via the `dlctl ingest` command. If a version for the current date already exists, it will output an error and do nothing—just wait a millisecond.

#### Manual

For manually uploaded datasets, you can create a directory in S3 by giving it the dataset name:

```bash
dlctl ingest dataset --manual "Your Dataset Name"
```

This will create a directory like `s3://lakehouse/raw/your_dataset_name/2025_06_03/19_56_03_000`, update `s3://lakehouse/raw/your_dataset_name/manifest.json` to point to it, and print the path to stdout.

#### From Kaggle or Hugging Face

```bash
dlctl ingest dataset \
    "https://www.kaggle.com/datasets/<username>/<dataset>"

dlctl ingest dataset \
    "https://huggingface.co/datasets/<username>/<dataset>"
```

The dataset name will be automatically extracted from the `<dataset>` slug and transformed into snake case for storage. Then, a directory like `s3://lakehouse/raw/your_dataset_name/2025_06_03/19_56_03_000` will be created, `s3://lakehouse/raw/your_dataset_name/manifest.json` updated to point to it, and the final path printed to stdout.

#### Listing Ingested Datasets

You can also list existing dataset paths for the most recent version, to be used for transformation:

```bash
dlctl ingest ls
```

Or all of them:

```bash
dlctl ingest ls -a
```

#### Pruning Empty Datasets

Sometimes you'll manually create a dataset and never upload data into the directory, or an ingestion process from a URL will fail and leave an empty directory behind. You can prune those directories using:

```bash
dlctl ingest prune
```

### Transformation

Transformations can be done via `dlctl transform`, which will call `dbt` with the appropriate arguments:

```bash
dlctl transform "<dataset-name>"
```

### Export

#### Exporting to Parquet

In order to externally use a dataset from the Lakehouse, you first need to export it. This can be done for any data mart catalog, over a selected schema. Exported datasets will be kept in dated directories with their own `manifest.json`.

```bash
dlctl export dataset "<data-mart-catalog>" "<schema>"
```

#### Listing Exported Datasets

You can list the most recent versions of exported datasets:

```bash
dlctl export ls
```

Or all of them:

```bash
dlctl export ls -a
```

#### Pruning Empty Datasets

After a few exports, you might want to remove old versions to claim space. You can prune those directories using:

```bash
dlctl export prune
```

### Backup

Since we rely on embedded databases and S3 object storage, we need to backup our databases.

> [!IMPORTANT]
> Data Lab was designed to be used in an education or research environment, so it currently doesn't support concurrent users. This could easily be added, though, as DuckLake supports PostgreSQL catalogs in place of SQLite, which we are using here.

#### Create

You can create a backup by running:

```bash
dlctl backup create
```

#### Restore

In order to restore a backup, just run:

```bash
dlctl backup restore \
    --source "<YYYY-mm-ddTHH:MM:SS.sss>" \
    --target "<target-dir>"
```

Omitting `--source` will restore the latest backup.

> [!CAUTION]
> Omitting `--target` will restore to `local/` by default, so take care not to overwrite your working version by mistake!

#### List

You can list all backups using:

```bash
dlctl backup ls
```

And you can list all files in all backups using:

```bash
dlctl backup ls -a
```

### Graph

#### Load

This will load nodes and edges into a KùzuDB database stored under `local/graphs/<schema>`, where `schema` is a schema containing nodes and edges under the `graphs` data mart catalog. Table names for nodes or edges are usually prefixed with `<dataset>_nodes_` or `<dataset>_edges_`, respectively, and should follow the format described on KùzuDB's docs.

```bash
dlctl graph load "<schema>"
```

#### Compute

A collection of graph computation calls will live here. These can be wrappers to native KùzuDB computations, or external computations. Currently, we just include the `embeddings` computation, which runs in Python using PyTorch. This will compute FRP embeddings with dimension 256, over batches of 9216 nodes, trained using 5 epochs, for the `<schema>` graph:

```bash
dlctl graph compute embeddings "<schema>" -d 256 -b 9216 -e 5
```
