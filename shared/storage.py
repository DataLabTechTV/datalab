import json
import os
from datetime import datetime, timezone
from enum import Enum
from fnmatch import fnmatch

import boto3
from loguru import logger as log
from slugify import slugify

from shared.settings import env

MANIFEST = "manifest.json"
IGNORE_PATTERNS = (".keep", "README", "*.md", MANIFEST)


class StoragePrefix(Enum):
    INGEST = 1
    EXPORTS = 2


class Storage:
    def __init__(self):
        endpoint = env.str("S3_ENDPOINT", required=False)
        use_ssl = env.bool("S3_USE_SSL", default=True)
        access_key = env.str("S3_ACCESS_KEY_ID")
        secret_key = env.str("S3_SECRET_ACCESS_KEY")
        region = env.str("S3_REGION")

        if endpoint is None:
            endpoint_url = None
        else:
            endpoint_url = f"https://{endpoint}" if use_ssl else f"http://{endpoint}"

        self.s3 = boto3.resource(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

        bucket_name = env.str("S3_BUCKET")
        ingest_prefix = env.str("S3_INGEST_PREFIX")
        exports_prefix = env.str("S3_EXPORTS_PREFIX")

        if bucket_name is None:
            raise ValueError("S3_BUCKET not defined")

        if ingest_prefix is None:
            raise ValueError("S3_INGEST_PREFIX not defined")

        if exports_prefix is None:
            raise ValueError("S3_EXPORTS_PREFIX not defined")

        self.ingest_prefix = ingest_prefix.strip("/")
        self.exports_prefix = exports_prefix.strip("/")

        bucket = self.s3.Bucket(bucket_name)

        if bucket not in self.s3.buckets.all():
            raise FileNotFoundError("Bucket does not exist: {}", self.bucket.name)

        self.bucket = bucket

    def to_s3_path(self, prefix: str) -> str:
        return f"s3://{self.bucket.name}/{prefix}"

    def from_s3_path(self, s3_path: str) -> str:
        prefix = "/".join(s3_path.split("/")[3:])
        return prefix

    def from_storage_prefix(self, prefix: StoragePrefix) -> str:
        match prefix:
            case StoragePrefix.INGEST:
                s3_prefix = self.ingest_prefix
            case StoragePrefix.EXPORTS:
                s3_prefix = self.exports_prefix

        return s3_prefix

    def get_dir(
        self,
        ds_name: str,
        dated: bool = False,
        upload_placeholder: bool = False,
        prefix: StoragePrefix = StoragePrefix.INGEST,
    ) -> str:
        s3_prefix = f"{self.from_storage_prefix(prefix)}/{ds_name}"

        if dated:
            now = datetime.now(timezone.utc)
            date_str = now.strftime("%Y_%m_%d")
            time_str = now.strftime("%H_%M_%S_%f")[:-3]
            s3_prefix += f"/{date_str}/{time_str}"

        s3_path = self.to_s3_path(s3_prefix)

        if upload_placeholder:
            try:
                log.info("Creating S3 directory placeholder: {}", s3_path)
                self.bucket.put_object(Key=f"{s3_prefix}/.keep")
            except:
                raise IOError(f"Could not create directory placeholder: {s3_path}")

        return s3_path

    def upload_files(self, source_path: str, s3_target_path: str):
        s3_target_prefix = self.from_s3_path(s3_target_path)

        file_paths = []

        for root, _, files in os.walk(source_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, source_path)
                file_paths.append(relative_path)

        log.info("Uploading {} files to {}", len(file_paths), s3_target_path)

        for file_path in file_paths:
            local_path = os.path.join(source_path, file_path)
            log.info(f"Uploading {local_path} to {s3_target_path}/{file_path}")

            self.bucket.upload_file(
                Filename=local_path,
                Key=f"{s3_target_prefix}/{file_path}",
            )

    def download_file(self, s3_source_path: str, target_path: str):
        s3_source_prefix = self.from_s3_path(s3_source_path)

        log.info("Downloading {} to {}", s3_source_path, target_path)

        self.bucket.download_file(
            Key=s3_source_prefix,
            Filename=target_path,
        )

    def upload_manifest(
        self,
        ds_name: str,
        *,
        latest: str,
        prefix: StoragePrefix = StoragePrefix.INGEST,
    ):
        log.info("Setting latest for {} as {}", ds_name, latest)

        data = json.dumps(
            {
                "dataset": ds_name,
                "latest": latest,
            }
        )

        prefix = self.from_storage_prefix(prefix)

        self.bucket.put_object(
            Key=f"{prefix}/{ds_name}/{MANIFEST}",
            Body=data,
            ContentType="application/json",
        )

    def latest_to_env(self):
        s3_ingest_prefix = env.str("S3_INGEST_PREFIX")

        for obj in self.bucket.objects.all():
            key_parts = obj.key.strip("/").split("/")

            if key_parts[0] != s3_ingest_prefix:
                continue

            if key_parts[-1] != MANIFEST:
                continue

            manifest = json.loads(obj.get().get("Body").read().decode("utf-8"))

            data_objects = self.bucket.objects.filter(
                Prefix=self.from_s3_path(manifest["latest"])
            )

            for data_obj in data_objects:
                is_ignorable = any(
                    fnmatch(data_obj.key.split("/")[-1], ignore_pattern)
                    for ignore_pattern in IGNORE_PATTERNS
                )

                if is_ignorable:
                    continue

                env_prefix_parts = key_parts[:2] + [
                    slugify(kp, separator="_") for kp in key_parts[4:]
                ]

                env_prefix = "__".join(env_prefix_parts).upper()

                os.environ[env_prefix] = self.to_s3_path(data_obj.key)

    def ls(self, prefix: StoragePrefix, include_all: bool = False) -> list[str]:
        prefix = self.from_storage_prefix(prefix)

        listing = {}

        for obj in self.bucket.objects.filter(Prefix=prefix):
            key_parts = obj.key.strip("/").split("/")

            if key_parts[-1] != MANIFEST:
                continue

            manifest = json.loads(obj.get().get("Body").read().decode("utf-8"))

            if include_all:
                s3_dataset_path = "/".join(
                    self.from_s3_path(manifest["latest"]).split("/")[:2]
                )

                data_objects = self.bucket.objects.filter(Prefix=s3_dataset_path)
            else:
                data_objects = self.bucket.objects.filter(
                    Prefix=self.from_s3_path(manifest["latest"])
                )

            listing[manifest["dataset"]] = []

            for data_obj in data_objects:
                is_ignorable = any(
                    fnmatch(data_obj.key.split("/")[-1], ignore_pattern)
                    for ignore_pattern in IGNORE_PATTERNS
                )

                if is_ignorable:
                    continue

                listing[manifest["dataset"]].append(data_obj.key)

        for dataset, files in listing.items():
            print(dataset)
            print("=" * len(dataset))
            print()

            for file in files:
                print(file)

            print()

    def prune(self, prefix: StoragePrefix) -> int:
        prefix = self.from_storage_prefix(prefix)

        for obj in self.bucket.objects.filter(Prefix=prefix):
            key_parts = obj.key.strip("/").split("/")

            if key_parts[-1] != MANIFEST:
                continue

            manifest = json.loads(obj.get().get("Body").read().decode("utf-8"))

            dataset_prefix = "/".join(
                self.from_s3_path(manifest["latest"]).split("/")[:2]
            )

            latest_prefix = self.from_s3_path(manifest["latest"])

            for data_obj in self.bucket.objects.filter(Prefix=dataset_prefix):
                if data_obj.key.startswith(latest_prefix):
                    continue

                if len(data_obj.key.split("/")) < 4:
                    # <prefix>/<dataset>/<date>/<time>
                    continue

                log.info("Deleting {}", data_obj.key)
                data_obj.delete()
