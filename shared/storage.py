import json
import os
from datetime import datetime, timezone
from enum import Enum
from fnmatch import fnmatch
from typing import Any, Iterable, Optional

import boto3
from loguru import logger as log
from mypy_boto3_s3.service_resource import Bucket
from slugify import slugify

from shared.settings import env

MANIFEST = "manifest.json"
IGNORE_PATTERNS = (".keep", "README", "*.md", MANIFEST)


class StoragePrefix(Enum):
    INGEST = 1
    EXPORTS = 2
    BACKUPS = 3


class Storage:
    def __init__(self, prefix: StoragePrefix):
        self.endpoint = env.str("S3_ENDPOINT", required=False)
        self.use_ssl = env.bool("S3_USE_SSL", default=True)
        self.access_key = env.str("S3_ACCESS_KEY_ID")
        self.secret_key = env.str("S3_SECRET_ACCESS_KEY")
        self.region = env.str("S3_REGION")

        if self.endpoint is not None:
            self.endpoint = (
                f"https://{self.endpoint}"
                if self.use_ssl
                else f"http://{self.endpoint}"
            )

        match prefix:
            case StoragePrefix.INGEST:
                self.prefix = env.str("S3_INGEST_PREFIX").strip("/")
            case StoragePrefix.EXPORTS:
                self.prefix = env.str("S3_EXPORTS_PREFIX").strip("/")
            case StoragePrefix.BACKUPS:
                self.prefix = env.str("S3_BACKUPS_PREFIX").strip("/")

        log.debug("Using prefix: {}", self.prefix)

        self._bucket = None

    @property
    def bucket(self) -> Bucket:
        if self._bucket is None:
            s3 = boto3.resource(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )

            bucket = s3.Bucket(env.str("S3_BUCKET"))

            if bucket not in s3.buckets.all():
                raise FileNotFoundError("Bucket does not exist: {}", bucket.name)

            self._bucket = bucket

        return self._bucket

    def to_s3_path(self, prefix: str) -> str:
        return f"s3://{self.bucket.name}/{prefix}"

    def from_s3_path(self, s3_path: str) -> str:
        prefix = "/".join(s3_path.split("/")[3:])
        return prefix

    def get_dir(
        self,
        ds_name: str,
        dated: bool = False,
        upload_placeholder: bool = False,
    ) -> str:
        s3_prefix = f"{self.prefix}/{ds_name}"

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

    def upload_files(
        self,
        source_root: str,
        source_files: Iterable[str],
        s3_target_path: str,
    ):
        s3_target_prefix = self.from_s3_path(s3_target_path)

        source_files = list(source_files)

        log.info("Uploading {} files to {}", len(source_files), s3_target_path)

        for source_path in source_files:
            local_path = os.path.join(source_root, source_path)
            log.info(f"Uploading {local_path} to {s3_target_path}/{source_path}")

            self.bucket.upload_file(
                Filename=local_path,
                Key=f"{s3_target_prefix}/{source_path}",
            )

    def upload_dir(self, source_path: str, s3_target_path: str):
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

    def download_dir(self, s3_source_path: str, target_path: str):
        s3_source_prefix = self.from_s3_path(s3_source_path)

        count = 0

        for obj in self.bucket.objects.filter(Prefix=s3_source_prefix):
            relative_path = obj.key[len(s3_source_prefix) :]

            if not relative_path:
                continue

            local_path = os.path.join(target_path, relative_path.lstrip("/"))
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            log.info("Downloading {} to {}", self.to_s3_path(obj.key), local_path)
            self.bucket.download_file(Key=obj.key, Filename=local_path)

            count += 1

        if count == 0:
            log.warning("No files were found in {}", s3_source_path)

    def upload_manifest(
        self,
        ds_name: str,
        *,
        latest: str,
    ):
        log.info("Setting latest for {} as {}", ds_name, latest)

        data = json.dumps(
            {
                "dataset": ds_name,
                "latest": latest,
            }
        )

        self.bucket.put_object(
            Key=f"{self.prefix}/{ds_name}/{MANIFEST}",
            Body=data,
            ContentType="application/json",
        )

    def load_manifest(self, path: str) -> Optional[dict[str, Any]]:
        obj = self.bucket.Object(f"{self.prefix}/{path}/{MANIFEST}")

        try:
            manifest = json.loads(obj.get().get("Body").read().decode("utf-8"))
        except:
            return

        return manifest

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
                key_parts = os.path.splitext(data_obj.key)[0].split("/")

                is_ignorable = any(
                    fnmatch(key_parts[-1], ignore_pattern)
                    for ignore_pattern in IGNORE_PATTERNS
                )

                if is_ignorable:
                    continue

                env_prefix_parts = key_parts[:2] + [
                    slugify(kp, separator="_") for kp in key_parts[4:]
                ]

                env_prefix = "__".join(env_prefix_parts).upper()

                os.environ[env_prefix] = self.to_s3_path(data_obj.key)

    def ls(
        self,
        include_all: bool = False,
        display: bool = True,
    ) -> dict[str, list[str]]:
        listing = {}

        for obj in self.bucket.objects.filter(Prefix=self.prefix):
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

        if display:
            for dataset, files in listing.items():
                print(dataset)
                print("=" * len(dataset))
                print()

                for file in files:
                    print(file)

                print()

        return listing

    def prune(self) -> int:
        for obj in self.bucket.objects.filter(Prefix=self.prefix):
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

                if len(data_obj.key.split("/")) <= 4:
                    # <prefix>/<dataset>/<date>/<time>
                    continue

                log.info("Deleting {}", data_obj.key)
                data_obj.delete()
