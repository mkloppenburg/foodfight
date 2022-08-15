""" this communication part is heavily borrowed from
    django-messages: https://github.com/arneb/django-messages/
    And adapted to fit the Player model"""

from django import forms
#from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from player.models import Player
from .models import Message
from .helpers import check_recipients


class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = forms.CharField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject"), max_length=140)
    body = forms.CharField(label=_(u"Body"), widget=forms.Textarea(
        attrs={
            'rows': '12',
            'cols':'55'
            }
        ))

    def __init__(self, *args, **kwargs):
        super(ComposeForm, self).__init__(*args, **kwargs)
        self.recipients_list = []

    def save(self, sender, parent_msg=None):
        """ function to save a message """
        recipients = self.recipients_list
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for recipient in recipients:
            msg = Message(
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = timezone.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
        return message_list

    def clean_recipient(self):
        """ check if valid player names have been entered """
        recipients = self.cleaned_data['recipient']
        recipients = check_recipients(recipients)
        for recipient in recipients:
            try:
                recipient = Player.objects.all().get(player__iexact=recipient, active=True)
                self.recipients_list.append(recipient)
            except Player.DoesNotExist:
                raise forms.ValidationError(_("Player isn't alive or does not exist."),
                                            code='not_a_player')
        return self.recipients_list
