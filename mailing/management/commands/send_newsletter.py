import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing, MailingAttempt

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Обработка и отправка активных рассылок"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mailing-id", type=int, help="ID конкретной рассылки для отправки"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Принудительная отправка независимо от времени",
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Тестовый режим (не создает MailingAttempt)",
        )

    def handle(self, *args, **options):
        mailing_id = options.get("mailing_id")
        test_mode = options.get("test")

        now = timezone.now()

        if mailing_id:
            mailings = Mailing.objects.filter(id=mailing_id)
            if not mailings.exists():
                self.stdout.write(
                    self.style.ERROR(f"Рассылка с ID {mailing_id} не найдена")
                )
                return
        else:
            mailings = Mailing.objects.filter(
                status__in=["created", "running"],
                start_time__lte=now,
                end_time__gte=now,
            )

        if not mailings.exists():
            self.stdout.write(self.style.WARNING("Нет активных рассылок для отправки"))
            return

        total_processed = 0
        total_emails_sent = 0

        for mailing in mailings:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nОбработка рассылки #{mailing.id}: "{mailing.message.subject}"'
                )
            )

            if mailing.status != "running":
                mailing.status = "running"
                mailing.save()

            recipients = mailing.recipients.all()
            self.stdout.write(f"Получателей: {recipients.count()}")

            mailing_sent = 0
            mailing_failed = 0

            for recipient in recipients:
                try:
                    if test_mode:
                        self.stdout.write(
                            f"[ТЕСТ] Отправка для: {recipient.full_name} ({recipient.email})"
                        )
                        mailing_sent += 1
                    else:
                        success = self.send_email_to_recipient(mailing, recipient)

                        if success:
                            mailing_sent += 1
                            MailingAttempt.objects.create(
                                datetime_attempt=now,
                                status="success",
                                mail_server_response="Успешно отправлено",
                                mailing=mailing,
                            )
                        else:
                            mailing_failed += 1
                            MailingAttempt.objects.create(
                                datetime_attempt=now,
                                status="failed",
                                mail_server_response="Ошибка отправки",
                                mailing=mailing,
                            )

                except Exception as e:
                    mailing_failed += 1
                    logger.error(f"Ошибка отправки для {recipient.email}: {str(e)}")

                    if not test_mode:
                        MailingAttempt.objects.create(
                            datetime_attempt=now,
                            status="failed",
                            mail_server_response=str(e),
                            mailing=mailing,
                        )

                    self.stdout.write(
                        self.style.ERROR(f"✗ Ошибка для {recipient.email}: {str(e)}")
                    )

            if mailing_sent > 0 and mailing_failed == 0:
                mailing.status = "completed"
                mailing.save()

            total_processed += 1
            total_emails_sent += mailing_sent

            self.stdout.write(
                self.style.SUCCESS(
                    f"Рассылка #{mailing.id} завершена: "
                    f"Успешно: {mailing_sent}, Ошибок: {mailing_failed}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nОБРАБОТКА ЗАВЕРШЕНА!\n"
                f"Обработано рассылок: {total_processed}\n"
                f"Всего отправлено писем: {total_emails_sent}"
            )
        )

    def send_email_to_recipient(self, mailing, recipient):
        """Отправка email конкретному получателю"""
        try:
            message = mailing.message

            email_body = message.body.replace("{full_name}", recipient.full_name)
            email_body = email_body.replace("{email}", recipient.email)

            email_subject = message.subject

            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Отправлено: {recipient.full_name} ({recipient.email})"
                )
            )
            return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Ошибка отправки для {recipient.email}: {str(e)}")
            )
            return False
