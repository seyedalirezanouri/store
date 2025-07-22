from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import re

def user_directory_path(instance, filename): 
    return 'user_{0}/{1}'.format(instance.id, filename) 

def validate_phone_number(value):
    if not re.match(r'^09\d{9}$', value):
        raise ValidationError('Phone number must be 11 digits long and start with 09.')
    
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True, validators=(validate_phone_number,))
    profile_image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    class Meta: 
        constraints = [
            models.UniqueConstraint(
                fields=['phone_number'],
                condition=models.Q(phone_number__isnull=False) & ~models.Q(phone_number__exact=''),
                name='phone_number_unique'
            )
        ]
