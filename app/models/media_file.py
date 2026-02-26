import uuid

from django.db import models

from app.models.base import BaseModel


class MediaFile(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey("app.Account", on_delete=models.CASCADE, related_name="media_files")
    account_id: int
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="media_files")
    user_id: uuid.UUID
    file_name = models.CharField(max_length=255, unique=True, db_index=True)
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, default="application/octet-stream")
    size = models.BigIntegerField()
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "media_files"

    def __str__(self):
        return self.file_name
