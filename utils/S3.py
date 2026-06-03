# utils/s3.py
import boto3
from botocore.exceptions import ClientError
from config import Config


def get_s3_client():
    missing = [
        name for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "AWS_S3_BUCKET")
        if not getattr(Config, name)
    ]
    if missing:
        raise RuntimeError(f"Missing AWS S3 configuration: {', '.join(missing)}")

    return boto3.client(
        "s3",
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_REGION,
    )


def upload_file_to_s3(local_path: str, s3_key: str) -> str:
    """
    Uploads a local file to S3 and returns the public URL.
    """
    client = get_s3_client()
    try:
        client.upload_file(local_path, Config.AWS_S3_BUCKET, s3_key)
    except ClientError as e:
        raise RuntimeError(f"S3 upload failed: {e}")

    url = f"https://{Config.AWS_S3_BUCKET}.s3.{Config.AWS_REGION}.amazonaws.com/{s3_key}"
    return url

def delete_file_from_s3(s3_key: str) -> None:
    """
    Deletes a file from S3 using its key.
    """
    client = get_s3_client()
    try:
        client.delete_object(Bucket=Config.AWS_S3_BUCKET, Key=s3_key)
    except ClientError as e:
        raise RuntimeError(f"S3 delete failed: {e}")

def upload_pdf_to_s3(local_path: str, s3_key: str) -> str:
    """
    Uploads a PDF file to S3 and returns the S3 key.
    """
    client = get_s3_client()
    try:
        client.upload_file(
            local_path,
            Config.AWS_S3_BUCKET,
            s3_key,
            ExtraArgs={"ContentType": "application/pdf"},
        )
    except ClientError as e:
        raise RuntimeError(f"S3 PDF upload failed: {e}")
    return s3_key


def download_pdf_from_s3(s3_key: str) -> bytes:
    """
    Downloads a PDF from S3 and returns its bytes.
    """
    client = get_s3_client()
    try:
        response = client.get_object(Bucket=Config.AWS_S3_BUCKET, Key=s3_key)
        return response["Body"].read()
    except ClientError as e:
        raise RuntimeError(f"S3 download failed: {e}")


def generate_presigned_url(s3_key: str, expiry_seconds: int = 3600) -> str:
    """
    Generates a presigned URL for a PDF stored in S3.
    Defaults to 1 hour expiry.
    """
    client = get_s3_client()
    try:
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": Config.AWS_S3_BUCKET, "Key": s3_key},
            ExpiresIn=expiry_seconds,
        )
    except ClientError as e:
        raise RuntimeError(f"Failed to generate presigned URL: {e}")
    return url