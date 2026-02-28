"""
AWS S3 Uploader Service
"""

import asyncio
import logging
import os
from pathlib import Path
import aioboto3
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger(__name__)


class S3Uploader:

    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.region = settings.AWS_REGION
        self.session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    async def upload_file(self, local_path: str, s3_key: str) -> str:
        """
        Upload a file to S3 and return the public URL.
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"File not found: {local_path}")

        if not settings.AWS_ACCESS_KEY_ID:
            logger.warning("⚠️ No AWS credentials configured, returning local path")
            return f"file://{local_path}"

        content_type = self._guess_content_type(local_path)
        file_size = os.path.getsize(local_path)
        logger.info(f"⬆️ Uploading to S3: {s3_key} ({file_size / 1024 / 1024:.1f} MB)")

        try:
            async with self.session.client("s3") as s3:
                await s3.upload_file(
                    local_path,
                    self.bucket,
                    s3_key,
                    ExtraArgs={
                        "ContentType": content_type,
                        "ACL": "public-read",
                    },
                )

            url = self._build_url(s3_key)
            logger.info(f"✅ Uploaded to S3: {url}")
            return url

        except ClientError as e:
            logger.error(f"❌ S3 upload failed: {e}")
            raise

    async def delete_file(self, s3_key: str):
        """Delete a file from S3."""
        async with self.session.client("s3") as s3:
            await s3.delete_object(Bucket=self.bucket, Key=s3_key)
        logger.info(f"🗑️ Deleted from S3: {s3_key}")

    async def get_presigned_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for secure temporary access."""
        async with self.session.client("s3") as s3:
            url = await s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=expires_in,
            )
        return url

    def _build_url(self, s3_key: str) -> str:
        if settings.S3_BASE_URL:
            return f"{settings.S3_BASE_URL.rstrip('/')}/{s3_key}"
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"

    @staticmethod
    def _guess_content_type(path: str) -> str:
        ext = Path(path).suffix.lower()
        types = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        return types.get(ext, "application/octet-stream")
