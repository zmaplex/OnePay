# Register your models here.
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
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
    list_display = ['name', 'enable', 'reload_gateway']

    def reload_gateway(self, instance):
        return mark_safe('<a href="/api/PayGateway/BaseGateway/reload_plugin/" target="_blank">重载</a>')

    reload_gateway.short_description = "重新加载"
