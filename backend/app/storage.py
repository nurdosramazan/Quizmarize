import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from .config import settings

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ROOT_USER,
            aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
            config=Config(signature_version="s3v4")
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    def upload_file(self, file_object, object_name: str, content_type: str):
        try:
            self.s3_client.upload_fileobj(
                file_object,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': content_type}
            )
            # We can construct the URL manually for MinIO
            file_url = f"http://localhost:9000/{self.bucket_name}/{object_name}"
            return file_url
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return None

    def ensure_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except self.s3_client.exceptions.ClientError as e:
            # 404 = bucket does not exist
            if e.response['Error']['Code'] == '404':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                self.s3_client.put_bucket_policy(
                    Bucket=self.bucket_name,
                    Policy=f'{{"Version":"2012-10-17","Statement":[{{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::{self.bucket_name}/*"}}]}}'
                )
            else:
                raise

# Create a single instance to be used across the app
storage_service = StorageService()