import os

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from mailing.models import Mailing
from recipients.models import Recipient
from users.forms import UserProfileForm, UserRegisterForm
from users.models import User


def custom_logout(request):
    logout(request)
    return redirect("/")


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = True
        user.save()
        send_mail(
            subject="Регистрация на сайте",
            message="Спасибо за регистрацию!",
            from_email=os.getenv("EMAIL_HOST_USER"),
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/user_profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен!")
        return super().form_valid(form)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/user_profile.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        return self.request.user


class UserMailingStatisticsView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "users/user_statistics.html"
    context_object_name = "object_list"  # важно для таблицы

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and hasattr(user, "role") and user.role == "manager":
            queryset = Mailing.objects.all()
        elif user.is_authenticated:
            queryset = Mailing.objects.filter(owner=user)
        else:
            queryset = Mailing.objects.none()

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated and hasattr(user, "role") and user.role == "manager":
            total_mailings = Mailing.objects.count()
            active_mailings = Mailing.objects.filter(status="running").count()
            unique_clients = Recipient.objects.distinct().count()
        elif user.is_authenticated:
            total_mailings = Mailing.objects.filter(owner=user).count()
            active_mailings = Mailing.objects.filter(
                owner=user, status="running"
            ).count()
            unique_clients = Recipient.objects.filter(owner=user).distinct().count()
        else:
            total_mailings = 0
            active_mailings = 0
            unique_clients = 0

        context.update(
            {
                "total_mailings": total_mailings,
                "active_mailings": active_mailings,
                "unique_clients": unique_clients,
            }
        )

        return context
