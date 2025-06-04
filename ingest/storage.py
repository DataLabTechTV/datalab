import json
import os
from datetime import datetime, timezone

import boto3
from dotenv import load_dotenv
from loguru import logger as log


class Storage:
    def __init__(self):
        load_dotenv()

        endpoint_url = os.getenv("S3_ENDPOINT_URL")
        access_key = os.getenv("S3_ACCESS_KEY")
        secret_key = os.getenv("S3_SECRET_KEY")
        region = os.getenv("S3_REGION")

        self.s3 = boto3.resource(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

        bucket_name = os.getenv("S3_BUCKET")
        ingest_prefix = os.getenv("S3_INGEST_PREFIX")

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

    def mkdir(self, path: str, dated: bool = False) -> str:
        path = path.strip("/")

        s3_prefix = f"{self.ingest_prefix}/{path}"

        if dated:
            now = datetime.now(timezone.utc)
            date_str = now.strftime("%Y_%m_%d")
            time_str = now.strftime("%H_%M_%S_%f")[:-3]
            s3_prefix += f"/{date_str}/{time_str}"

        s3_path = self.to_s3_path(s3_prefix)

        try:
            log.info("Creating S3 directory: {}", s3_path)
            self.bucket.put_object(Key=f"{s3_prefix}/.keep")
            return s3_path
        except:
            raise IOError(f"Could not create directory: {s3_path}")

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

    def set_latest(self, path: str, latest_s3_path: str):
        path = path.strip("/")
        log.info("Setting latest as {}", latest_s3_path)

        data = json.dumps({"latest": latest_s3_path})

        self.bucket.put_object(
            Key=f"{self.ingest_prefix}/{path}/latest.json",
            Body=data,
            ContentType="application/json",
        )
