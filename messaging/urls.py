from django.urls import path

from messaging.apps import MessagingConfig
from messaging.views import (
    MessageCreateView,
    MessageDeleteView,
    MessageListView,
    MessageUpdateView,
)

app_name = MessagingConfig.name

urlpatterns = [
    path("messaging/", MessageListView.as_view(), name="messages_list"),
    path("messaging/create/", MessageCreateView.as_view(), name="message_form"),
    path("messaging/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_edit"),
    path(
        "messaging/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
]
