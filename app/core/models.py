from django.db import models  # noqa
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)  # noqa

from . import constants


class UserManager(BaseUserManager):
    """Manager for user model"""

    def create_user(self, email, password=None, **extra_fields):
        # create, save & return a new user
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        # create, save & return a new superuser
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.role = constants.TYPE_ADMIN

        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        max_length=10, choices=constants.USER_ROLES, default=constants.TYPE_USER  # noqa
    )

    # assigning a custom manager to the user model
    objects = UserManager()

    USERNAME_FIELD = "email"


class Recipe(models.Model):
    # Recipe object blue print
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # noqa
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField("Tag")

    def __str__(self):
        return self.title


class Tag(models.Model):
    # Tag object blue print
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
