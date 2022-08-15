""" Decorators for the player model """
from django.http import HttpResponseRedirect
from player.models import Player

def alive_player_required(function):
    """
    decorator to check for an active player for the logged in user.
    returns the active player if there is one.
    Special thanks to kezabelle & knbk on #django for pointing me in the kwargs direction
    """
    def wrapper(request, *args, **kwargs):
        try:
            player = Player.objects.all().get(user=request.user, active=True)
            kwargs['player'] = player
            if player.alive is False:
                return HttpResponseRedirect('/player_dead')
        except Player.DoesNotExist:
            return HttpResponseRedirect('/create_player')
        return function(request, *args, **kwargs)
    return wrapper
