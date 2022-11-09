from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import validate_username


ROLES = (
    ('user', 'user'),
    ('moderator', 'moderator'),
    ('admin', 'admin'),
)


class User(AbstractUser):
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        max_length=150,
        blank=True)
    last_name = models.CharField(
        max_length=150,
        blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    confirmation_code = models.CharField(
        max_length = 8,
        default='100000'
    )
