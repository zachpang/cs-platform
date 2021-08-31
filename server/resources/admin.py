from django.contrib import admin

from .models import Quota, Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "owner")


class QuotaInline(admin.TabularInline):
    model = Quota
    can_delete = False
