from pathlib import Path

from django.conf import settings
from rest_framework import serializers

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/csv",
    "application/zip",
}

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".pdf",
    ".csv",
    ".zip",
}


class UploadMediaRequestSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if value.size > settings.STORAGE_MAX_UPLOAD_SIZE:
            max_size_megabytes = settings.STORAGE_MAX_UPLOAD_SIZE // (1024 * 1024)

            raise serializers.ValidationError(f"File size exceeds the maximum allowed size of {max_size_megabytes} MB.")

        sanitized_name = Path(value.name).name
        if not sanitized_name or sanitized_name.startswith("."):
            raise serializers.ValidationError("Invalid file name.")
        value.name = sanitized_name

        extension = Path(sanitized_name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(f"File type '{extension}' is not allowed.")

        if value.content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(f"Content type '{value.content_type}' is not allowed.")

        return value
