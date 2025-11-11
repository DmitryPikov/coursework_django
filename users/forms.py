from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field, forms.ModelMultipleChoiceField):
                field.widget.attrs["class"] = "form-select multiple-select"
            else:
                field.widget.attrs["class"] = "form-control"
            if field.required:
                field.error_messages = {
                    "required": "Это поле обязательно для заполнения"
                }
            field.widget.attrs["placeholder"] = field.label


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    email = forms.EmailField(
        label="Электронная почта",
        help_text="Введите адрес электронной почты",
    )
    password1 = forms.CharField(
        label="Пароль",
        help_text="Введите пароль",
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        help_text="Введите пароль ещё раз",
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        labels = {
            "email": "Электронная почта",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }


class UserProfileForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]  # Добавьте нужные поля
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }
