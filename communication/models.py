""" this communication part is heavily borrowed from
    django-messages: https://github.com/arneb/django-messages/
    And adapted to fit the Player model"""


from django.db import models
from django.utils.translation import ugettext_lazy as _
from player.models import Player


class Message(models.Model):
    """
    A private message from user to user
    """
    subject = models.CharField(_("Subject"), max_length=140)
    body = models.TextField(_("Body"))
    sender = models.ForeignKey(Player, related_name='sent_messages',
                               verbose_name=_("Sender"), on_delete=models.CASCADE)
    recipient = models.ForeignKey(Player, related_name='received_messages',
                                  null=True, blank=True, verbose_name=_("Recipient"),
                                  on_delete=models.CASCADE)
    parent_msg = models.ForeignKey('self', related_name='next_messages',
                                   null=True, blank=True, verbose_name=_("Parent message"),
                                   on_delete=models.SET_NULL)
    # time fields for the message
    sent_at = models.DateTimeField(_("sent at"), auto_now_add=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
    sender_deleted_at = models.DateTimeField(_("Sender deleted at"), null=True, blank=True)
    recipient_deleted_at = models.DateTimeField(_("Recipient deleted at"), null=True, blank=True)

    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is not None:
            return False
        return True

    def replied(self):
        """returns whether the recipient has written a reply to this message"""
        if self.replied_at is not None:
            return True
        return False

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


def inbox_count_for(user):
    """
    returns the number of unread messages for the given user but does not
    mark them seen
    """
    return Message.objects.filter(recipient=user, read_at__isnull=True,
                                  recipient_deleted_at__isnull=True).count()
