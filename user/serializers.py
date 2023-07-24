from rest_framework import serializers

from user.models import SmartLockUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartLockUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'encode']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = SmartLockUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = SmartLockUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()