"""Forms for the account app"""
from django import forms
#from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
#from .models import User
from .models import Player


class CreatePlayerForm(forms.Form):
    """form for creating a new player"""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreatePlayerForm, self).__init__(*args, **kwargs)

    player = forms.CharField(
        label=_("Player name"),
        max_length=32
    )

    def clean_player(self):
        """ function to do additional cleaning of the player name """
        player = self.cleaned_data.get("player")

        active_players = Player.objects.filter(user=self.user, active=True)
        if active_players:
            raise forms.ValidationError(
                _("You already have an active player"), code='user_has_player')

        forbidden = ["fuck", "cock"]
        if any(player in s for s in forbidden):
            raise forms.ValidationError(
                _(f"The name {player} is not allowed."), code='name_not_allowed')

        usernames = Player.objects.filter(player__iexact=player)
        if usernames:
            raise forms.ValidationError(
                _(f"The name {player} already exists"), code='player_already_exists')
        else:
            return player


class UpdatePlayerForm(forms.ModelForm):
    """ Form to update the player profile """
    description = forms.CharField(required=False, widget=forms.Textarea(
        attrs={
            'class': 'form control',
            'rows': '5',
        }
    ))
    image = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={
            'class': 'form-control-file',
        }
    ))

    class Meta:
        model = Player
        fields = ('description', 'image',)
