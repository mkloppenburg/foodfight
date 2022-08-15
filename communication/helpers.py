""" Utils file from django-messages """
from django.utils.text import wrap
from django.utils.translation import ugettext_lazy as _


def format_quote(sender, body):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(body, 55).split('\n')
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    quote = '\n'.join(lines)
    return _(u"%(sender)s wrote:\n%(body)s") % {
        'sender': sender,
        'body': quote
    }


def check_recipients(recipients):
    """ function to generate a list of players to send messages to. """
    recipients = recipients.replace(" ", "")
    recipients = recipients.split(",")
    return recipients
