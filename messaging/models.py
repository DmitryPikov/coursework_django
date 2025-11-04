from django.db import models

from users.models import User


class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")
    topic_message = models.CharField(max_length=150, verbose_name="Тема сообщения")
    text_message = models.TextField(max_length=500, verbose_name="Текст сообщения")

    def __str__(self):
        return f"{self.topic_message}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
