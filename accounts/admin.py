from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from .models import User

@register(User)
class CustomUserAdmin(UserAdmin):
    pass

CustomUserAdmin.fieldsets +=  (('Other Fields', {'fields': ('profile_image', 'phone_number')}),)
