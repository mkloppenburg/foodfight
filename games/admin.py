""" file for registering games models to the admin """
from django.contrib import admin
from .models import Item, PlayerItem

# Register your models here.
admin.site.register(Item)
admin.site.register(PlayerItem)
