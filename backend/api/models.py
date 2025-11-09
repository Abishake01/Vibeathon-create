from django.db import models
import uuid


def generate_uuid():
    """Generate a UUID string for model defaults."""
    return str(uuid.uuid4())


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    hashed_password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'


class Project(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid, editable=False)
    user_id = models.CharField(max_length=36, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'

