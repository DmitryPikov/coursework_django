from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from permissions import OwnerEditPermissionMixin, OwnerQuerysetMixin
from recipients.models import Recipient


class MainView(TemplateView):
    template_name = "users/main.html"


@method_decorator(cache_page(60 * 15), name="dispatch")
class RecipientListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Recipient
    template_name = "recipients/recipients_list.html"


@method_decorator(cache_page(60 * 15), name="dispatch")
class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "recipients/recipient_form.html"
    success_url = reverse_lazy("recipients:recipients_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


@method_decorator(cache_page(60 * 15), name="dispatch")
class RecipientUpdateView(
    LoginRequiredMixin,
    OwnerEditPermissionMixin,
    OwnerQuerysetMixin,
    UpdateView,
):
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "recipients/recipient_form.html"
    success_url = reverse_lazy("recipients:recipients_list")


@method_decorator(cache_page(60 * 15), name="dispatch")
class RecipientDeleteView(
    LoginRequiredMixin,
    OwnerEditPermissionMixin,
    OwnerQuerysetMixin,
    DeleteView,
):
    model = Recipient
    template_name = "recipients/recipient_confirm_delete.html"
    success_url = reverse_lazy("recipients:recipients_list")
