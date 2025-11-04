from django.urls import path

from recipients.apps import UsersConfig
from recipients.views import (
    RecipientCreateView,
    RecipientDeleteView,
    RecipientListView,
    RecipientUpdateView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("recipients/", RecipientListView.as_view(), name="recipients_list"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipients/<int:pk>/edit/",
        RecipientUpdateView.as_view(),
        name="recipient_edit",
    ),
    path(
        "recipients/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
]
