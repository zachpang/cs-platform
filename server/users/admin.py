"""
Due to custom EmailUser model implementation, django-admin forms and ModelAdmin classes
need to be overriden.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import EmailUser


class EmailUserChangeForm(UserChangeForm):
    class Meta:
        """
        Override Meta class to use custom EmailUser
        """

        model = EmailUser
        fields = "__all__"


class EmailUserCreationForm(UserCreationForm):
    class Meta:
        """
        Override Meta class to use custom EmailUser
        """

        model = EmailUser
        fields = ("email",)


@admin.register(EmailUser)
class EmailUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
