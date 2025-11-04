from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from mailing.models import Mailing
from mailing.services import send_mailing
from messaging.models import Message
from permissions import (
    ManagerRequiredMixin,
    OwnerEditPermissionMixin,
    OwnerQuerysetMixin,
)
from recipients.models import Recipient
from users.models import User


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Mailing
    template_name = "mailing/mailings_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()

        for mailing in queryset:
            attempts = mailing.attempts.all()
            total = attempts.count()
            successful = attempts.filter(status="success").count()
            failed = attempts.filter(status="failed").count()
            success_rate = (successful / total * 100) if total > 0 else 0

            mailing.stats = {
                "total": total,
                "successful": successful,
                "failed": failed,
                "success": round(success_rate, 2),
            }

        return queryset


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailings_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not (
            hasattr(self.request.user, "role") and self.request.user.role == "manager"
        ):
            form.fields["recipients"].queryset = Recipient.objects.filter(
                owner=self.request.user
            )
            form.fields["message"].queryset = Message.objects.filter(
                owner=self.request.user
            )
        return form


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingUpdateView(
    LoginRequiredMixin,
    OwnerEditPermissionMixin,
    OwnerQuerysetMixin,
    UpdateView,
):
    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailings_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not (
            hasattr(self.request.user, "role") and self.request.user.role == "manager"
        ):
            form.fields["recipients"].queryset = Recipient.objects.filter(
                owner=self.request.user
            )
            form.fields["message"].queryset = Message.objects.filter(
                owner=self.request.user
            )
        return form


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingDeleteView(
    LoginRequiredMixin,
    OwnerEditPermissionMixin,
    OwnerQuerysetMixin,
    DeleteView,
):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailings_list")


@method_decorator(cache_page(60 * 15), name="dispatch")
class ManagerUserListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = User
    template_name = "mailing/manager_users_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return User.objects.all().order_by("-date_joined")


@method_decorator(cache_page(60 * 15), name="dispatch")
class ManagerMailingListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/manager_mailings_list.html"
    context_object_name = "mailings"
    paginate_by = 20


@method_decorator(cache_page(60 * 15), name="dispatch")
class ManagerRecipientListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/manager_recipients_list.html"
    context_object_name = "recipients"
    paginate_by = 20


def toggle_user_block(request, user_id):
    if not (hasattr(request.user, "role") and request.user.role == "manager"):
        messages.error(request, "У вас нет прав для выполнения этого действия")
        return redirect("mailing:mailings_list")

    user = get_object_or_404(User, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()

    action = "заблокирован" if user.is_blocked else "разблокирован"
    messages.success(request, f"Пользователь {user.username} {action}")
    return redirect("mailing:manager_users")


def toggle_mailing_status(request, mailing_id):
    if not (hasattr(request.user, "role") and request.user.role == "manager"):
        messages.error(request, "У вас нет прав для выполнения этого действия")
        return redirect("mailing:mailings_list")

    mailing = get_object_or_404(Mailing, id=mailing_id)
    if mailing.status == "disabled":
        mailing.status = "created"
        action = "включена"
    else:
        mailing.status = "disabled"
        action = "отключена"
    mailing.save()

    messages.success(request, f"Рассылка #{mailing.id} {action}")
    return redirect("mailing:manager_mailings")


def index(request):
    user = request.user

    if user.is_authenticated and hasattr(user, "role") and user.role == "manager":
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(status="running").count()
        unique_clients = Recipient.objects.distinct().count()
    elif user.is_authenticated:
        total_mailings = Mailing.objects.filter(owner=user).count()
        active_mailings = Mailing.objects.filter(owner=user, status="running").count()
        unique_clients = Recipient.objects.filter(owner=user).distinct().count()
    else:
        total_mailings = 0
        active_mailings = 0
        unique_clients = 0

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_clients": unique_clients,
    }

    return render(request, "users/main.html", context)


def start_mailing(request, mailing_id):
    mailing = get_object_or_404(Mailing, id=mailing_id)

    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.is_blocked:
        messages.error(
            request, "Ваш аккаунт заблокирован. Вы не можете запускать рассылки."
        )
        return redirect("mailing:mailings_list")

    if hasattr(request.user, "role") and request.user.role == "manager":
        messages.error(request, "Менеджеры не могут запускать рассылки")
        return redirect("mailing:mailings_list")

    if mailing.owner != request.user:
        messages.error(request, "Вы можете запускать только свои рассылки")
        return redirect("mailing:mailings_list")

    if mailing.status == "disabled":
        messages.error(request, "Эта рассылка отключена менеджером")
        return redirect("mailing:mailings_list")

    results = send_mailing(mailing)
    messages.success(
        request,
        f"Рассылка завершена. Успешно: {results['success']}, Неудачно: {results['failed']}",
    )
    return redirect("mailing:mailings_list")
