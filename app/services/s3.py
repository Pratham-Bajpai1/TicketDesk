import logging

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings

logger = logging.getLogger("ticketdesk.s3")


def get_s3_client():
    """
    Create an S3 client using the ECS Task Role credentials automatically.

    - In ECS/Fargate: credentials come from the Task Role.
    - Locally: credentials can come from AWS CLI or environment variables.
    """
    region = settings.AWS_REGION or "ap-southeast-1"

    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url=f"https://s3.{region}.amazonaws.com",
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "virtual"}
        )
    )


def generate_presigned_upload_url(
    file_key: str,
    content_type: str = "application/octet-stream",
    expires_in: int = 3600,
) -> str:
    """
    Generate a real S3 presigned PUT URL for direct browser uploads.
    """

    bucket_name = settings.s3_bucket_name

    try:
        s3_client = get_s3_client()

        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": file_key,
            },
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )

        logger.info(f"Generated presigned upload URL for {file_key}")
        return url

    except (BotoCoreError, ClientError) as e:
        logger.exception("Failed to generate S3 presigned URL")
        raise RuntimeError("Could not generate upload URL") from e