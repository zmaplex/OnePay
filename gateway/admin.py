# Register your models here.
from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from gateway.models import *


@admin.register(PayApplication)
class PayApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ['own', 'app_id', 'platform_private_key']


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ['name', 'sid', 'app', 'gateway', 'status']


@admin.register(PayGateway)
class PayGatewayAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
