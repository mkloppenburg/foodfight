"""
Forms for the games app

The following tutorial was very helpful in creating this form:
https://jacobian.org/writing/dynamic-form-generation/

"""
from re import sub
from django import forms
from django.utils.translation import ugettext_lazy as _
from games.models import PlayerItem
from player.models import Player

class FeedForm(forms.Form):
    """ Form to feed other players """
    def __init__(self, player, *args, **kwargs):
        super(FeedForm, self).__init__(*args, **kwargs)
        self.player = player
        # retrieve objects with a positive and negative effect
        get_items = PlayerItem.objects.filter(player=player)

        if get_items:
            for i, item in enumerate(get_items):
                if item.amount >= 1:
                    self.fields['custom_%s' % i] = forms.IntegerField(
                        required=False,
                        label=f"{item.item.item} (you have: {item.amount})",
                        min_value=1,
                        max_value=item.amount
                        )

    def feed_items(self):
        """ function to return all used items to the view """
        for name, value in self.cleaned_data.items():
            if name.startswith('custom_'):
                item_dirty = self.fields[name].label
                # run regex (remove the amount) and remove spaces on the end of the string
                item = sub(r'\([^)]*\)', '', item_dirty).rstrip()
                yield (item, value)

class FeedSomeoneForm(forms.Form):
    """ Form to feed other players """
    # The following tutorial was very helpful in creating this form:
    # https://jacobian.org/writing/dynamic-form-generation/
    player_to_feed = forms.CharField(
        label=_("Feed player:"),
        max_length=32
    )
    def __init__(self, player, *args, **kwargs):
        super(FeedSomeoneForm, self).__init__(*args, **kwargs)
        self.player = player
        # only retrieve the objects with a negative effect
        get_items = PlayerItem.objects.filter(player=player, item__effect__contains='-')

        if get_items:
            for i, item in enumerate(get_items):
                if item.amount >= 1:
                    self.fields['custom_%s' % i] = forms.IntegerField(
                        required=False,
                        label=f"{item.item.item} (you have: {item.amount})",
                        min_value=1,
                        max_value=item.amount
                        )

    def feed_items(self):
        """ function to return all used items to the view """
        for name, value in self.cleaned_data.items():
            if name.startswith('custom_'):
                item_dirty = self.fields[name].label
                # run regex (remove the amount) and remove spaces on the end of the string
                item = sub(r'\([^)]*\)', '', item_dirty).rstrip()
                yield (item, value)

    def clean_player_to_feed(self):
        """ function to do additional cleaning of the player name """
        to_feed = self.cleaned_data.get("player_to_feed")
        try:
            player_to_feed = Player.objects.all().get(player=to_feed, active=True)
        except Player.DoesNotExist:
            raise forms.ValidationError(
                _(f"Please enter a valid player name! (not {to_feed}!)"), code='fed_unknown')
        if self.player == player_to_feed:
            raise forms.ValidationError(
                _("You can't feed this crap to yourself here!"), code='fed_myself')
        else:
            return player_to_feed
