from rest_framework import serializers

from gateway.models import PayApplication


class PayApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayApplication
        exclude = ['merchant_public_key', 'platform_private_key']
