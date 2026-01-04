from minio import Minio
from django.conf import settings
from minio.error import S3Error


def upload_to_minio(file, file_name):
    """
    Загружает файл на MinIO.
    """
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_HTTPS
    )

    try:
        if not client.bucket_exists(
            settings.MINIO_BUCKET_NAME
        ):
            client.make_bucket(
                settings.MINIO_BUCKET_NAME
            )

        client.put_object(
            settings.MINIO_BUCKET_NAME,
            file_name,
            file,
            length=file.size,
            content_type=file.content_type
        )

        return f"https://{
            settings.MINIO_ENDPOINT
        }/{settings.MINIO_BUCKET_NAME}/{file_name}"

    except S3Error as e:
        print(f"Ошибка при загрузке файла на MinIO: {e}")
        return None


def delete_from_minio(file_name):
    """
    Удаляет файл с MinIO.
    """
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_HTTPS
    )

    try:
        client.remove_object(
            settings.MINIO_BUCKET_NAME, file_name
        )
        return True
    except S3Error as e:
        print(f"Ошибка при удалении файла с MinIO: {e}")
        return False
