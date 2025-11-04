from django.core.mail import send_mail
from django.utils import timezone

from mailing.models import Mailing, MailingAttempt


def send_mailing(mailing):
    """
    Отправляет рассылку и создает записи о попытках отправки
    """
    success_count = 0
    failed_count = 0

    mailing.status = "running"
    mailing.save()

    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.topic_message,
                message=mailing.message.text_message,
                from_email=None,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            MailingAttempt.objects.create(
                datetime_attempt=timezone.now(),
                status="success",
                mail_server_response="Успешно отправлено",
                mailing=mailing,
            )
            success_count += 1

        except Exception as e:
            MailingAttempt.objects.create(
                datetime_attempt=timezone.now(),
                status="failed",
                mail_server_response=str(e)[:250],
                mailing=mailing,
            )
            failed_count += 1

    mailing.status = "completed"
    mailing.save()

    return {"success": success_count, "failed": failed_count}


def get_all_mailings_statistics():
    """
    Получает статистику по всем рассылкам
    """
    mailings = Mailing.objects.all()
    statistics = []

    for mailing in mailings:
        attempts = mailing.attempts.all()
        total_attempts = attempts.count()
        successful_attempts = attempts.filter(status="success").count()
        failed_attempts = attempts.filter(status="failed").count()

        statistics.append(
            {
                "mailing": mailing,
                "stats": {
                    "total": total_attempts,
                    "success": successful_attempts,
                    "failed": failed_attempts,
                    "success_rate": (
                        (successful_attempts / total_attempts * 100)
                        if total_attempts > 0
                        else 0
                    ),
                },
            }
        )

    return statistics
