from django.urls import path

from mailing.apps import MailingConfig
from mailing.views import (MailingCreateView, MailingDeleteView,
                           MailingListView, MailingUpdateView, start_mailing)

app_name = MailingConfig.name

urlpatterns = [
    path("mailing/", MailingListView.as_view(), name="mailings_list"),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_form"),
    path("mailing/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing_edit"),
    path(
        "mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path("mailing/<int:mailing_id>/start/", start_mailing, name="start_mailing"),
]
