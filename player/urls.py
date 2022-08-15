""" URLS for the player part of the game """
from django.urls import path
from player.views import all_players, create_player, index, player_dead
from player.views import player_profile, terminate_player, update_player

# urls patterns for the different views needed for the player app
urlpatterns = [
    path("", index, name="index"),
    path("create_player", create_player, name="create_player"),
    path("update_player", update_player, name="update_player"),
    path("all_players", all_players, name="all_players"),
    path("player_dead", player_dead, name="player_dead"),
    path("terminate_player", terminate_player, name="terminate_player"),
    path("player_profile/<int:player_id>", player_profile, name="player_profile"),
]
