# Data Lab

Tooling for a minimalist data lab running on top of DuckLake.


## Components

### ingest/

### transform/

### local/

### logs/

### dlctl


## Ingestion

As a rule of thumb, ingestion will be done via the `dlctl ingest` command. If a version for the current date already exists, it will output an error and do nothing—just wait a second.

### Manual

For manually uploaded datasets, you can create a directory in S3 by giving it the dataset name:

```bash
dlctl ingest --standalone --dataset "Your Dataset Name"
```

This will create a directory `s3://lakehouse/raw/your_dataset_name/2025-06-03/19-56-03` and print the path to stdout.

### Kaggle

### Hugging Face

### Other

### 🗃️ Storage Layout

All data is stored in a single S3 bucket (e.g., `s3://lakehouse`, tested with MinIO), with directory structure:

```
s3://lakehouse/
├── catalog/
│   └── backups/
├── raw/
│   └── <dataset-name>/
│       └── YYYY-MM-DD/
│           └── HH-mm-SS/
│               ├── *.csv
│               ├── *.json
│               └── *.parquet
├── stage/
│   └── <dataset-name>/
│           └── *.parquet
├── marts/
│   └── <domain>/
│           └── *.parquet
└── logs/
```

## Transformation

Transformations can be run via `dlctl transform`, which will run:

```bash
cd transform/ && dbt run
```
