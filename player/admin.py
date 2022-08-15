""" Admin extensions for the player section """
from django.contrib import admin
from .models import Player, Rank

# Register your models here.

admin.site.register(Player)
admin.site.register(Rank)
