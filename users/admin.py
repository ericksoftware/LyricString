from django.contrib import admin
from .models import CustomUser, UserPreferences

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(UserPreferences)