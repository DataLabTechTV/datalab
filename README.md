# Data Lab

Tooling for a minimalist data lab running on top of DuckLake.

## 🗃️ Storage Layout

All data is stored in an S3 bucket (tested with MinIO), in a single bucket (e.g., `s3://lakehouse`) with directory structure:

```
s3://lakehouse/
├── catalog.sqlite
├── raw/
│   └── <dataset-name>/
│       └── YYYY-MM-DD/
│           ├── *.csv
│           ├── *.json
│           └── *.parquet
├── stage/
│   └── <dataset-name>/
│           └── *.parquet
├── marts/
│   └── <domain>/
│           └── *.parquet
└── logs/
```
