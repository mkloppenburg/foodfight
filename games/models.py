""" Models for the games part of the site """
from django.db import models
from player.models import Player
# Create your models here.


class Item(models.Model):
    """
    An in-game item.
    """
    item = models.CharField(max_length=140)
    effect = models.IntegerField(default=0)

class PlayerItem(models.Model):
    """
    Items belonging to the player
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='player_items')
    amount = models.IntegerField(default=0)
