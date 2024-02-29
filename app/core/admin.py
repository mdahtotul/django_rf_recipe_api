"django admin customization"

from django.contrib import admin  # noqa
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  # noqa
from django.utils.translation import gettext_lazy as _  # noqa
from . import models  # noqa

"""
email: admin@example.com
pass: 1234
"""


class UserAdmin(BaseUserAdmin):
    # Define the admin pages for users
    ordering = ["id"]
    list_display = ["email", "name", "role"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "role")},
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    readonly_fields = ["last_login"]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "role",
                ),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
