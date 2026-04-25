from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def get_contact_from_email():
    return getattr(settings, "CONTACT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)


def get_contact_notify_emails(message=None):
    """
    Ordem de prioridade:
    1. E-mail da categoria, se houver.
    2. CONTACT_NOTIFY_EMAILS no settings.py.
    """

    if message and message.category and message.category.email_to:
        return [message.category.email_to]

    return getattr(settings, "CONTACT_NOTIFY_EMAILS", [])


def send_new_contact_notification(message):
    recipients = get_contact_notify_emails(message)

    if not recipients:
        return 0

    subject = f"Nova mensagem de contato: {message.subject}"

    body = render_to_string(
        "contacts/emails/new_contact_notification.txt",
        {"message": message},
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=get_contact_from_email(),
        to=recipients,
        reply_to=[message.email],
    )

    return email.send(fail_silently=True)


def send_contact_reply_email(message):
    subject = f"Resposta ao seu contato: {message.subject}"

    body = render_to_string(
        "contacts/emails/contact_reply.txt",
        {"message": message},
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=get_contact_from_email(),
        to=[message.email],
    )

    return email.send(fail_silently=False)