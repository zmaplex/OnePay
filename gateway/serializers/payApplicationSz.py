from rest_framework import serializers

from gateway.models import PayApplication


class PayApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayApplication
        fields = '__all__'
