import json
import os
from datetime import datetime, timezone
from fnmatch import fnmatch

import boto3
from loguru import logger as log
from slugify import slugify

from shared.settings import env

MANIFEST = "manifest.json"
IGNORE_PATTERNS = (".keep", "README", "*.md", MANIFEST)


class Storage:
    def __init__(self):
        endpoint = env.str("S3_ENDPOINT", required=False)
        use_ssl = env.bool("S3_USE_SSL", default=True)
        access_key = env.str("S3_ACCESS_KEY")
        secret_key = env.str("S3_SECRET_KEY")
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

        bucket_name = env.str("S3_BUCKET", default="lakehouse")
        ingest_prefix = env.str("S3_INGEST_PREFIX", default="raw")

        if bucket_name is None:
            raise ValueError("S3_BUCKET not defined")

        if ingest_prefix is None:
            raise ValueError("S3_INGEST_PREFIX not defined")

        self.ingest_prefix = ingest_prefix.strip("/")

        bucket = self.s3.Bucket(bucket_name)

        if bucket not in self.s3.buckets.all():
            raise FileNotFoundError("Bucket does not exist: {}", self.bucket.name)

        self.bucket = bucket

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
        s3_prefix = f"{self.ingest_prefix}/{ds_name}"

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

    def upload_manifest(self, ds_name: str, *, latest: str):
        log.info("Setting latest for {} as {}", ds_name, latest)

        data = json.dumps(
            {
                "dataset": ds_name,
                "latest": latest,
            }
        )

        self.bucket.put_object(
            Key=f"{self.ingest_prefix}/{ds_name}/{MANIFEST}",
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
