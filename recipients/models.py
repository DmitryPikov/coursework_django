from django.conf import settings
from django.db import models


class Recipient(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    email = models.EmailField(max_length=254, unique=True)
    full_name = models.CharField(max_length=150, verbose_name="Ф.И.О.")
    comment = models.TextField(max_length=500, blank=True, verbose_name="Комментарий")

    def __str__(self):
        return f"{self.full_name}"

    class Meta:
        permissions = [
            ("can_view_all_recipients", "Может просматривать всех клиентов"),
        ]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
