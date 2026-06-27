from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import AuditInfo

from .managers import UserManager


class Role(AuditInfo):
    ADMIN_USER = 'Admin'
    STANDARD_USER = 'Standard'
    ACCESS_LEVEL_CHOICES = [
        (ADMIN_USER, 'Admin'),
        (STANDARD_USER, 'Standard'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES)
    seeded = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def for_email(cls, email: str) -> 'Role':
        normalized = email.strip().lower()
        code = 'ADMIN_USER' if normalized.endswith('@nebula-corp.com') else 'STANDARD_USER'
        return cls.objects.get(code=code)


class User(AbstractUser):
    objects = UserManager()

    username = None
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20, null=True, blank=True, default='')
    role = models.ForeignKey(
        Role,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    @property
    def access_level(self):
        if self.role:
            return self.role.access_level
        return None
