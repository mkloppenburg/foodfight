""" URLS for the communication part of the game """
from django.urls import path
from .views import inbox, outbox, send_message
from .views import reply_message, read_message, trash, delete_message, restore_message

# urls patterns for the different views needed for communication
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
