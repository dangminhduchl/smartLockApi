from rest_framework import serializers
from user.models import SmartLockUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartLockUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'encode']


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    class Meta :
        model = SmartLockUser
        fields = ('old_password', 'new_password')
    def validate_old_password(self, value):
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        return value


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
