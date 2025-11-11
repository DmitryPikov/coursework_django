from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from messaging.models import Message
from permissions import OwnerEditPermissionMixin, OwnerQuerysetMixin


class MessageListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Message
    template_name = "messaging/messages_list.html"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ["topic_message", "text_message"]
    template_name = "messaging/message_form.html"
    success_url = reverse_lazy("messaging:messages_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(
    LoginRequiredMixin,
    OwnerEditPermissionMixin,
    OwnerQuerysetMixin,
    UpdateView,
):
    model = Message
    fields = ["topic_message", "text_message"]
    template_name = "messaging/message_form.html"
    success_url = reverse_lazy("messaging:messages_list")


class MessageDeleteView(
    LoginRequiredMixin,
    OwnerEditPermissionMixin,
    OwnerQuerysetMixin,
    DeleteView,
):
    model = Message
    template_name = "messaging/message_confirm_delete.html"
    success_url = reverse_lazy("messaging:messages_list")
