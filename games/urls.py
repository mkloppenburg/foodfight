""" URLS for the player part of the game """
from django.urls import path
from .views import do_game, eat, feed_someone, games, items

# Url paths for the player app
urlpatterns = [
    path("do_game/<int:game_id>", do_game, name="do_game"),
    path("eat", eat, name="eat"),
    path("feed_someone", feed_someone, name="feed_someone"),
    path("games", games, name="games"),
    path("items", items, name="items"),
]
