""" Views for the games of the website """
from random import randint, choice
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from player.decorators import alive_player_required
from communication.models import Message
from games.models import Item, PlayerItem
from games.forms import FeedForm, FeedSomeoneForm
from games.helpers import get_rank_skill_odds


# Create your views here.
@login_required
@alive_player_required
def games(request, player):
    """ main view to start a game from """
    context = {
        "player": player,
    }
    return render(request, "games/games.html", context)

@login_required
@alive_player_required
def do_game(request, player, game_id):
    """ view to start a specific game

    for the games the win chances are determined upon:
    base odds (the higher the game, the lower)
    player rank
    amount of played games

    It's calculated as following:
    There are 5 ranks, which count from 1-5
    There are 5 skill levels, counted from 0-4
    so rank * skill is a random scope deduction of 20.

    The odds are semi random, with odds improving with rank and skill:
    randint(0, (100 - (player.rank.id * skill)))
    """
    # set item variable to be used later on
    item = False

    # first check if the player is allowed to start a game (once every 4 min/240sec).
    if player.last_game:
        timecheck = int((timezone.now() - player.last_game).total_seconds())
        if timecheck < 240:
            timeleft = 240 - timecheck
            messages.error(request, _(f"You need to wait {timeleft} seconds to start a new game"))
            return redirect('games')

    # get the odds enhancer for the player
    rank_skill_odds = get_rank_skill_odds(player)

    if game_id is 1:
        # perhaps a faster alternative for randint can be implemented?
        if randint(0, 100) < (50 + rank_skill_odds):
            item = choice(Item.objects.filter(Q(effect__lte=6), Q(effect__gte=-6)))
    elif game_id is 2:
        if randint(0, 100) < (40 + rank_skill_odds):
            item = choice(Item.objects.filter(Q(effect__lte=11), Q(effect__gte=-6)))
    elif game_id is 3:
        if randint(0, 100) < (30 + rank_skill_odds):
            item = choice(Item.objects.all())
    else:
        raise Http404

    if not item:
        messages.error(request, _("Better luck next time!"))

    if item:
        update_item, created = PlayerItem.objects.get_or_create(player=player, item=item)
        update_item.amount += 1
        update_item.save()
        print(created)
        messages.success(request, _(f"You won: {item.item}"))
        item = False

    # update the player statistics after a run that didn't end prematurely
    player.games_done = player.games_done + 1
    # timezone.now sets the time to the server time.
    player.last_game = timezone.now()
    player.save()
    # refresh the player with the up-to-date time
    player.refresh_from_db()

    return redirect('games')

@login_required
@alive_player_required
def items(request, player):
    """ view to show all the items the player has """
    items_list = list(PlayerItem.objects.filter(player=player))

    context = {
        "items_list": items_list,
        "player": player,
    }
    return render(request, "games/items.html", context)


@login_required
@alive_player_required
@never_cache
def feed_someone(request, player):
    """ view to feed another player """
    # check if the player has items to use
    # change this to be filled into the form later on?
    if PlayerItem.objects.filter(player=player,
                                 item__effect__contains='-', amount__gte='1').exists():
        has_items = True
    else:
        has_items = False
    # get the odds enhancer for the player
    rank_skill_odds = get_rank_skill_odds(player)

    if request.method == "POST":
        form = FeedSomeoneForm(player, request.POST)
        print("posted")
        if form.is_valid():
            player_to_feed = form.cleaned_data["player_to_feed"]
            total_health = 0
            for (item, amount) in form.feed_items():
                if amount:
                    check = PlayerItem.objects.get(player=player, item__item=item)
                    effect = check.item.effect * amount
                    total_health = total_health + effect
                    check.amount = check.amount - amount
                    check.save()
            if randint(0, 100) < (50 + rank_skill_odds):
                # this needs to add the total health (which is a negative!)
                player_to_feed.health = player_to_feed.health + total_health
                player_to_feed.save()
                player_to_feed.refresh_from_db()
                # check if the health of player to feed is 0 or less.
                if player_to_feed.health <= 0:
                    player_to_feed.alive = False
                    player_to_feed.died = timezone.now()
                    player_to_feed.killed_by = player
                    player_to_feed.save()
                    player_to_feed.refresh_from_db()
                    messages.success(request, _(f"You fed {player_to_feed} successfully "
                                                f"and did {total_health} to {player_to_feed}'s "
                                                "health! This unfortunately was too much for "
                                                f"{player_to_feed} and now his family "
                                                "will need to arrange a funeral."))
                else:
                    mail = Message(
                        subject="You have been fed!",
                        body=f"{player} fed you and did {total_health} damage!",
                        sender=player,
                        recipient=player_to_feed
                        )
                    mail.save()
                    messages.success(request, _(f"You fed {player_to_feed} successfully "
                                                f"and did {total_health} to {player_to_feed}'s"
                                                "health!"))
            else:
                mail = Message(
                    subject=f"{player} tried to feed you!",
                    body=f"{player} tried to feed you, but fortunately "
                         "you were fast enough and ran without getting hurt!",
                    sender=player,
                    recipient=player_to_feed
                    )
                mail.save()
                messages.error(request, _(f"Uhooh! To bad, {player_to_feed} ran superfast "
                                          "and you didn't succeed to feed him all that junk!"))
            return redirect('feed_someone')
    else:
        form = FeedSomeoneForm(player)

    context = {
        "form": form,
        "has_items": has_items,
        "player": player,
    }
    return render(request, "games/feed_someone.html", context)

@login_required
@alive_player_required
def eat(request, player):
    """ view to feed player """
    # check if the player has items to use
    # change this to be filled into the form later on?
    if PlayerItem.objects.filter(player=player, amount__gte='1').exists():
        has_items = True
    else:
        has_items = False
    if request.method == "POST":
        form = FeedForm(player, request.POST)
        if form.is_valid():
            total_health = 0
            for (item, amount) in form.feed_items():
                if amount:
                    check = PlayerItem.objects.get(player=player, item__item=item)
                    effect = check.item.effect * amount
                    total_health = total_health + effect
                    check.amount = check.amount - amount
                    check.save()
            # add total to player's health (be a positive or negative)
            # total health can never reach over 100
            if (player.health + total_health) > 100:
                total_health = (100-player.health)
            player.health = player.health + total_health
            player.save()
            player.refresh_from_db()
                # check if the health of player to feed is 0 or less.
            messages.success(request, _(f"You've added {total_health} to your health!"))
            return redirect('eat')
    else:
        form = FeedForm(player)

    context = {
        "form": form,
        "has_items": has_items,
        "player": player,
    }

    return render(request, "games/eat.html", context)
