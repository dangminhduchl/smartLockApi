from rest_framework import serializers
from .models import Request, Status


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    request = StatusSerializer()
    action = StatusSerializer()
    user_name = serializers.CharField(source='user.username')

    class Meta:
        model = Request
        fields = '__all__'
