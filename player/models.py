""" Models for setting up the player """
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


# Create your models here.
def user_profile_image_path(instance, filename):
    """ Function to create a proper path for profile image uploads """
    # file will be uploaded to MEDIA_ROOT/profile_images/<id>/<filename>
    return 'profile_images/{0}/{1}'.format(instance.user.id, filename)


def provide_deleted_player():
    """ function to help set None for on_delete """
    return None


class Rank(models.Model):
    """ Rank model """
    rank = models.IntegerField(unique=True)
    rank_decription = models.CharField(max_length=32, unique=True)
    games_needed = models.IntegerField(unique=False, default=0)


class Player(models.Model):
    """Player model."""
    # if user is deleted, also delete the player(s)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    player = models.CharField(max_length=32, unique=True)
    active = models.BooleanField(default=True)
    alive = models.BooleanField(default=True)
    died = models.DateTimeField(_("player died"), null=True, blank=True)
    killed_by = models.ForeignKey(
        "self",
        on_delete=models.SET(provide_deleted_player),
        related_name="killer",
        null=True)
    description = models.CharField(max_length=1000, blank=True)
    image = models.ImageField(upload_to=user_profile_image_path, blank=True)
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, related_name="player_rank", default=1)
    health = models.IntegerField(default=100)
    games_done = models.IntegerField(default=0)
    last_game = models.DateTimeField(_("last game"), null=True, blank=True)

    def save(self, *args, **kwargs):
        done = self.games_done
        try:
            rank_update = Rank.objects.get(games_needed=done)
            if rank_update:
                self.rank = rank_update
        except Rank.DoesNotExist:
            pass
        # Call the "real" save() method.
        super(Player, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.player}"
