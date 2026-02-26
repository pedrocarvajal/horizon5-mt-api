from pathlib import Path

import structlog
from django.conf import settings
from django.utils import timezone

from app.models import MediaFile

logger = structlog.get_logger("monitor")


class ExpiredMediaCleanup:
    name = "expired_media"

    def run(self):
        now = timezone.now()
        expired_files = MediaFile.objects.filter(expires_at__lt=now)
        deleted_count = 0
        errors = []

        for media_file in expired_files:
            file_path = (
                Path(settings.STORAGE_ROOT)
                / str(media_file.user_id)
                / "files"
                / media_file.created_at.strftime("%Y-%m-%d")
                / media_file.file_name
            )

            try:
                if file_path.is_file():
                    file_path.unlink()

                    parent_directory = file_path.parent
                    if parent_directory.is_dir() and not any(parent_directory.iterdir()):
                        parent_directory.rmdir()

                media_file.delete()
                deleted_count += 1
            except Exception as exc:
                errors.append({"file": media_file.file_name, "error": str(exc)})
                logger.error(
                    "expired_media_delete_failed",
                    file_name=media_file.file_name,
                    error=str(exc),
                )

        if deleted_count > 0:
            logger.info("expired_media_cleaned", deleted=deleted_count)
        else:
            logger.info("expired_media_ok", expired=0)

        status = "warning" if errors else "ok"

        return {
            "check": self.name,
            "deleted": deleted_count,
            "errors": len(errors),
            "status": status,
        }
