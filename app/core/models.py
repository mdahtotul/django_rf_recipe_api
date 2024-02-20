from django.db import models  # noqa
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)  # noqa

from . import constants


class UserManager(BaseUserManager):
    """Manager for user model"""

    def create_user(self, email, password=None, **extra_fields):
        "create, save & return a new user"
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        max_length=10, choices=constants.USER_ROLES, default=constants.TYPE_USER
    )

    # assigning a custom manager to the user model
    objects = UserManager()

    USERNAME_FIELD = "email"
