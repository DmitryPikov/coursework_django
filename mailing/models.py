from django.conf import settings
from django.db import models


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("running", "Запущена"),
        ("completed", "Завершена"),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        "messaging.Message", on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(
        "recipients.Recipient", verbose_name="Получатели"
    )

    class Meta:
        permissions = [
            ("can_view_all_mailings", "Может просматривать все рассылки"),
        ]
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]
    datetime_attempt = models.DateTimeField(verbose_name="Дата и время попытки")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    mail_server_response = models.TextField(max_length=250)
    mailing = models.ForeignKey(
        "mailing.Mailing",
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
        related_name="attempts",
    )
