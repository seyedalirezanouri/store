from rest_framework.serializers import ModelSerializer, CharField, ValidationError, Serializer, ImageField
from .models import User
from django.contrib.auth.password_validation import validate_password

class RegistrationSerializer(ModelSerializer):
    password = CharField(write_only=True)
    repeat_password = CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'repeat_password')
    
    def validate(self, data):
        if data['password'] != data['repeat_password']:
            raise ValidationError("Passwords must match!")
        validate_password(data['password'])
        return data

class ChangePasswordSerializer(Serializer):
    old_password = CharField(write_only=True)
    new_password = CharField(write_only=True)
    repeat_new_password = CharField(write_only=True)    
    
    def validate(self, data):
        if data['new_password'] != data['repeat_new_password']:
            raise ValidationError("Passwords must match!")
        validate_password(data['new_password'])
        return data
    
class SetProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'profile_image')
    def validate(self, data):
        phone_number = data.get('phone_number')
        if phone_number is not None and (len(phone_number) != 11 or not phone_number.startswith('09')):
            data.pop('phone_number')
        return data

class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_image', 'date_joined', 'is_active')
    