from django.contrib import admin

from messaging.models import Message
from recipients.models import Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "comment")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "topic_message", "text_message")
