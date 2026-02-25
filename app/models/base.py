from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def restore(self):
        return self.update(deleted_at=None)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def find(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None

    @classmethod
    def where(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    @classmethod
    def all(cls):
        return cls.objects.all()

    @classmethod
    def create(cls, **kwargs):
        return cls.objects.create(**kwargs)


class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    @classmethod
    def with_trashed(cls):
        return cls.all_objects.all()

    @classmethod
    def only_trashed(cls):
        return cls.all_objects.filter(deleted_at__isnull=False)
