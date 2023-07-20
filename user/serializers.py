from rest_framework import serializers
from django.contrib.auth.models import User

from user.models import SmartLockUser


class UserSerializer(serializers.ModelSerializer):
    encoding = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'encoding']

    def get_encoding(self, user):
        try:
            smart_lock_user = SmartLockUser.objects.get(id=user.id)
            return smart_lock_user.encoding
        except SmartLockUser.DoesNotExist:
            return False
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()