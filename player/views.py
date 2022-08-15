""" main views for the player segment of the game """
#from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from player.models import Player, Rank
from player.forms import CreatePlayerForm, UpdatePlayerForm
from player.decorators import alive_player_required


# Create your views here.
def index(request):
    """ this view manages the main index, including authorization """
    if not request.user.is_authenticated:
        return redirect('account_login')

    try:
        player = Player.objects.all().get(user=request.user, active=True)
    except Player.DoesNotExist:
        return redirect('create_player')

    if player.alive is False:
        return redirect('player_dead')

    rank_list = list(Rank.objects.filter())

    context = {
        'player': player,
        'rank_list': rank_list,
    }

    return render(request, "player/welcome.html", context)


@login_required
@alive_player_required
def player_profile(request, player_id, player):
    """ This view shows a player's profile """
    profile = None
    if player_id == player.id:
        is_player = True
        profile = player
    else:
        is_player = False
        try:
            profile = get_object_or_404(Player, id=player_id)
            print(profile)
        except Player.DoesNotExist:
            return redirect('index')

    context = {
        "is_player": is_player,
        "profile": profile,
        "player": player,
    }
    return render(request, "player/player_profile.html", context)


@login_required
def create_player(request):
    """ this view creates a new player if there isn't an active one """
    try:
        # if an active player already exists, return to index.
        player = Player.objects.all().get(user=request.user, active=True, alive=True)
        return redirect('index')
    except Player.DoesNotExist:
        pass

    form = CreatePlayerForm(request.POST or None, user=request.user)
    if form.is_valid():
        player = form.cleaned_data["player"]
        new_player = Player(user=request.user, player=player)
        new_player.save()
        return redirect('index')

    context = {
        'form': form
    }

    return render(request, "player/create_player.html", context)


@login_required
@alive_player_required
def update_player(request, player):
    """ This view allows updating the player profile page """
    if request.method == 'POST':
        # get the form and image file
        form = UpdatePlayerForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            if description:
                player.description = description
            if image:
                player.image = image
            player.save()
            messages.info(request, _(u"Profile successfully updated."))
            return redirect('index')
    else:
        if player.description is "":
            description = _("I still need to fill out this description!")
        else:
            description = player.description

        form = UpdatePlayerForm(initial={'description': description})

    context = {
        "form": form,
        "player": player,
    }

    return render(request, "player/update_player.html", context)


@login_required
@alive_player_required
def all_players(request, player):
    """ This view allows updating the player profile page """
    # add pagination
    players_list = list(Player.objects.all())

    context = {
        "players_list": players_list,
        "player": player,
    }

    return render(request, "player/all_players.html", context)


@login_required
def player_dead(request):
    """ A view for when a player dies """
    try:
        player = Player.objects.all().get(user=request.user, active=True, alive=False)
    except Player.DoesNotExist:
        return redirect('index')
    # an empty form needs to be displayed here to confirm the kill
    context = {
        "player": player,
    }
    return render(request, "player/player_dead.html", context)


@login_required
def terminate_player(request):
    """ view to set the player to inactive after player's dead """
    # first check if the player is in limbo
    try:
        player = Player.objects.all().get(user=request.user, active=True, alive=False)
    except Player.DoesNotExist:
        messages.warning(request, _(u"You cannot terminate this player!"))
        return redirect('index')
    # if so, kill the player
    player.active = False
    player.save()
    player.refresh_from_db()
    return redirect('index')
