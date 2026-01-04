# import uuid
# from django.core.files.storage import FileSystemStorage
# import os


# class UUIDFileSystemStorage(FileSystemStorage):

#     def get_available_name(self, name, max_length=None):

#         # Generate a UUID-based file name
#         ext = os.path.splitext(name)[1]
#         uuid_name = uuid.uuid4().hex + ext

#         # Get the directory from the original name
#         directory = os.path.dirname(name)

#         # Return the full path with the directory and the new UUID name
#         return os.path.join(directory, uuid_name)
