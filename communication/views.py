""" this communication part is heavily borrowed from
    django-messages: https://github.com/arneb/django-messages/
    And adapted to fit the Player model"""
# from datetime import datetime
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils import timezone
from player.decorators import alive_player_required
from .models import Message
from .forms import ComposeForm


@login_required
@alive_player_required
def inbox(request, player):
    """
    Display a list of received messages for the current player.
    """
    message_list = list(Message.objects.filter(
        recipient=player, recipient_deleted_at__isnull=True))

    context = {
        "message_list": message_list,
        "player": player,
    }
    return render(request, "communication/inbox.html", context)


@login_required
@alive_player_required
def outbox(request, player):
    """ Display a list of all messages sent by the current player. """
    message_list = list(Message.objects.filter(sender=player, sender_deleted_at__isnull=True))

    context = {
        "message_list": message_list,
        "player": player,
    }
    return render(request, "communication/outbox.html", context)


@login_required
@alive_player_required
def trash(request, player):
    """ Display a list of all messages deleted by the current player. """
    # upon loading trash, delete all messages that have been deleted by the sender and recipient.
    # perhaps adjust this later and make it a cronjob or move this to the delete part
    Message.objects.filter(sender_deleted_at__isnull=False,
                           recipient_deleted_at__isnull=False).delete()

    # https://docs.djangoproject.com/en/2.1/topics/db/queries/#complex-lookups-with-q-objects
    message_list = list(Message.objects.filter(
        Q(sender=player) & Q(sender_deleted_at__isnull=False) |
        Q(recipient=player) & Q(recipient_deleted_at__isnull=False)))

    context = {
        "message_list": message_list,
        "player": player,
    }
    return render(request, "communication/trash.html", context)


@login_required
@alive_player_required
def send_message(request, player):
    """ Displays a form to compose messages """
    form = ComposeForm(request.POST or None)
    if form.is_valid():
        form.save(sender=player)
        messages.info(request, _(u"Message successfully sent."))
        return redirect('inbox')

    context = {
        "form": form,
        "player": player,
    }

    return render(request, "communication/compose.html", context)


@login_required
@alive_player_required
def reply_message(request, message_id, player):
    """ Displays a prepopulated compose form """
    # retrieve the original message
    original = get_object_or_404(Message, id=message_id)
    if original.sender != player and original.recipient != player:
        print("error here")
        raise Http404

    if request.method == "POST":
        # send the reply if valid
        form = ComposeForm(request.POST)
        if form.is_valid():
            form.save(sender=player, parent_msg=original)
            messages.info(request, _(u"Message successfully sent."))
            return redirect('inbox')
    else:
        # show a prepopulated form
        form = ComposeForm(initial={
            'body': _('from: {} \n {}'.format(original.sender, original.body)),
            'subject': f"re: {original.subject}",
            'recipient': original.sender,
        })

    context = {
        "form": form,
        "player": player,
    }

    return render(request, "communication/compose.html", context)


@login_required
@alive_player_required
def read_message(request, message_id, player):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either
    the sender or the recipient. If the user is not allowed a 404
    is raised.
    If the user is the recipient and the message is unread
    ``read_at`` is set to the current datetime.
    If the user is the recipient a reply form will be added to the
    tenplate context, otherwise 'reply_form' will be None.
    """
    now = timezone.now()
    message = get_object_or_404(Message, id=message_id)
    if (message.sender != player) and (message.recipient != player):
        raise Http404
    if message.read_at is None and message.recipient == player:
        message.read_at = now
        message.save()

    if message.recipient == player:
        # sent_at = str(message.sent_at)
        # #sent_at = sent_at[:-12]
        # sent_at = datetime.strptime(sent_at, "%Y-%m-%d %H:%M:%S.%f+00:00")
        context = {
            'is_recipient': True,
            'one_message': message,
            'form': ComposeForm(initial={
                # 'body': _('from: {}\nto: {}\ndate: {}\nmessage:\n{}'.format(
                #     message.sender, message.recipient, message.sent_at, message.body)),
                'subject': _(f"Re: {message.subject}"),
                'recipient': message.sender,
            })}

    if message.sender == player:
        context = {'one_message': message, }

    if message.parent_msg is not None:
        parent_message = get_object_or_404(Message, id=message.parent_msg.id)
        context['parent_message'] = parent_message

    context['player'] = player

    return render(request, "communication/view.html", context)


@login_required
@alive_player_required
def delete_message(request, message_id, player):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely.
    A cron-job should prune the database and remove old messages which are
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.
    You can pass ?next=/foo/bar/ via the url to redirect the user to a different
    page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
    """

    now = timezone.now()
    message = get_object_or_404(Message, id=message_id)
    deleted = False
    if message.sender == player:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == player:
        message.recipient_deleted_at = now
        deleted = True
    # add an additional check here if both are deleted, remove the message completely
    if deleted:
        message.save()
        messages.info(request, _(u"Message successfully deleted."))
        return redirect('inbox')
    raise Http404


@login_required
@alive_player_required
def restore_message(request, message_id, player):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    message = get_object_or_404(Message, id=message_id)
    undeleted = False
    if message.sender == player:
        message.sender_deleted_at = None
        undeleted = True
    if message.recipient == player:
        message.recipient_deleted_at = None
        undeleted = True
    if undeleted:
        message.save()
        messages.info(request, _(u"Message successfully restored."))
        return redirect('inbox')
    raise Http404
