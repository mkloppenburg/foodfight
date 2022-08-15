""" URLS for the player part of the game """
from django.urls import path#, re_path
#from django.views.generic import RedirectView
from .views import inbox, outbox, send_message
from .views import reply_message, read_message, trash, delete_message, restore_message

urlpatterns = [
    path("inbox", inbox, name="inbox"),
    path("outbox", outbox, name="outbox"),
    path("send_message", send_message, name="send_message"),
    path("read_message/<int:message_id>", read_message, name="read_message"),
    path("reply_message/<int:message_id>", reply_message, name="reply_message"),
    path("delete_message/<int:message_id>", delete_message, name="delete_message"),
    path("restore_message/<int:message_id>", restore_message, name="restore_message"),
    path("trash", trash, name="trash"),
]
