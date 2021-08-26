"""
The original behavior of User model uses username field as an unique identifier.

Therefore, a custom User model need to be implemented to use email field as the unique
identifier (as required in the assignment)

See django docs:
https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#substituting-a-custom-user-model
"""

from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailUserManager(UserManager):
    """
    Since a custom User model is used in the application, we need to customize the
    UserManager class as well.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.__class__.normalize_email(email)  # call from class instead of self
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def create(self, **kwargs):
        """
        Overrides create() in QuerySet class so that EmailUser.objects.create()
        will route to create_user() in this class
        """
        return self.create_user(**kwargs)


class EmailUser(AbstractUser):
    """
    The original behavior of User model uses username field as an unique identifier.
    A custom User model is implemented to use email field as the unique identifier (as
    required in the assignment) by overriding django's AbstractUser
    """

    username = None
    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_(
            "Required. 254 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )

    objects = EmailUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
