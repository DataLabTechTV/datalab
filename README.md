# Data Lab

Tooling for a minimalist data lab running on top of DuckLake.


## Components

### ingest/

Helps manage ingestion from difference data sources, consisting only of the retrieval stage for raw data and the proper directory structure creation. Raw data might be dropped manually, from Kaggle, Hugging Face, or some other source. This will make it easy to load it and keep it organized.

### transform/

This is the core of the data lakehouse, using [dbt](https://docs.getdbt.com/) to transform raw data into usable data, with [DuckLake](https://ducklake.select/) as the underlying catalog, running on top of SQLite.

We purposely keep this simple with SQLite, using a backup/restore strategy to/from S3, as this assumes exploratory lab work, but you can easily replace [SQLite](https://ducklake.select/docs/stable/duckdb/usage/choosing_a_catalog_database#sqlite) with a [PostgreSQL](https://ducklake.select/docs/stable/duckdb/usage/choosing_a_catalog_database#postgresql) node, if you prefer.

### scripts/

Individual Bash or Python scripts for generic tasks, including catalog backup or restore.

### local/

Untracked directory where all your local files will live. This includes the DuckLake catalog, which you can load from a backup, or create from scratch.

### cli/

This is where the `dlctl` command lives—dlctl stands for 'Data Lab Control'. This helps you run all the tasks supported by the data lab package. It is available as a script under `pyproject.toml` that can be accessed via:

```bash
uv sync
source .venv/bin/activate
dlctl ...
```

> [!NOTE]
> A few `torch` dependencies, like `torch_sparse` require that `UV_FIND_LINKS` is set
> when adding/removing them, but not during install, where `uv.lock` already has the
> required information.
>
> ```bash
> export UV_FIND_LINKS="https://data.pyg.org/whl/torch-2.7.0+cu126.html"
> uv add --no-build-isolation pyg_lib torch_scatter torch_sparse \
>   torch_cluster torch_spline_conv
> ```

You should generate an `init.sql` once you setup your `.env`, so you can access your DuckLake from the CLI using `duckdb`:

```bash
dlctl tools generate-init-sql
duckdb -init local/init.sql local/engine.duckdb
```


## 🗃️ Storage Layout

All data is stored in a single S3 bucket (e.g., `s3://lakehouse`, tested with MinIO), with directory structure:

```
s3://lakehouse/
├── catalog/
│   ├── snapshots/
│   │   └── metadata-YYYY_MM_DD_HH_MM_SS_sss.sqlite
│   └── manifest.json
├── raw/
│   └── <dataset-name>/
│       ├── YYYY_MM_DD/
│       │   └── HH_mm_SS_sss/
│       │       ├── *.csv
│       │       ├── *.json
│       │       └── *.parquet
│       └── manifest.json
├── stage/
│   └── *.parquet
├── marts/
│   └── <domain>/
│           └── *.parquet
└── exports/
    └── <domain>/
        └── <dataset-name>/
            └── YYYY_MM_DD/
                └── HH_mm_SS_sss/
                    ├── *.csv
                    ├── *.json
                    └── *.parquet
```

> [!NOTE]
> Date/time entries should be always UTC.

## Ingestion

As a rule of thumb, ingestion will be done via the `dlctl ingest` command. If a version for the current date already exists, it will output an error and do nothing—just wait a millisecond.

### Manual

For manually uploaded datasets, you can create a directory in S3 by giving it the dataset name:

```bash
dlctl ingest dataset --manual "Your Dataset Name"
```

This will create a directory like `s3://lakehouse/raw/your_dataset_name/2025_06_03/19_56_03_000`, update `s3://lakehouse/raw/your_dataset_name/manifest.json` to point to it, and print the path to stdout.

### From Kaggle or Hugging Face

```bash
dlctl ingest dataset \
    "https://www.kaggle.com/datasets/<username>/<dataset>"

dlctl ingest dataset \
    "https://huggingface.co/datasets/<username>/<dataset>"
```

The dataset name will be automatically extracted from the `<dataset>` slug and transformed into snake case for storage. Then, a directory like `s3://lakehouse/raw/your_dataset_name/2025_06_03/19_56_03_000` will be created, `s3://lakehouse/raw/your_dataset_name/manifest.json` updated to point to it, and the final path printed to stdout.

### Listing Ingested Datasets

You can also list existing dataset paths for the most recent version, to be used for transformation:

```bash
dlctl ingest ls
```

Or all of them:

```bash
dlctl ingest ls -a
```

### Pruning Empty Datasets

Sometimes you'll manually create a dataset and never upload data into the directory, or an ingestion process from a URL will fail and leave an empty directory behind. You can prune those directories using:

```bash
dlctl ingest prune
```

## Transformation

Transformations can be done via `dlctl transform`, which will call `dbt` with the appropriate arguments:

```bash
dlctl transform "<dataset-name>"
```

## Exports

### Listing Exported Datasets

You can list the most recent versions of exported datasets:

```bash
dlctl exports ls
```

Or all of them:

```bash
dlctl exports ls -a
```

### Pruning Empty Datasets

After a few exports, you might want to remove old versions to claim space. You can prune those directories using:

```bash
dlctl exports prune
```
