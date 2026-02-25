from django.db import models


class SystemRole(models.TextChoices):
    ROOT = "root", "Root"
    PLATFORM = "platform", "Platform"
    PRODUCER = "producer", "Producer"
