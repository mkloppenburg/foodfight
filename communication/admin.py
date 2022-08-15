""" file for registering communication models to the admin """
from django.contrib import admin
from .models import Message

# Register your models here.
admin.site.register(Message)
