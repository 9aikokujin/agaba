import uuid
from django.core.files.storage import FileSystemStorage
import os


class UUIDFileSystemStorage(FileSystemStorage):
    """Хранилище файлов, подменяющее имя на UUID для уникальности."""

    def get_available_name(self, name, max_length=None):
        """Сгенерировать свободное имя файла, заменив базовое имя на UUID."""

        ext = os.path.splitext(name)[1]
        uuid_name = uuid.uuid4().hex + ext

        directory = os.path.dirname(name)

        return os.path.join(directory, uuid_name)
