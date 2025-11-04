import os

from django.contrib.auth import logout
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView

from users.forms import UserRegisterForm
from users.models import User


def custom_logout(request):
    logout(request)
    return redirect("/")


@method_decorator(cache_page(60 * 15), name="dispatch")
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
