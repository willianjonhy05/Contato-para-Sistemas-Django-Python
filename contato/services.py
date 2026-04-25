from django.db import transaction

from .emails import send_contact_reply_email, send_new_contact_notification


def register_new_contact_message(message):
    """
    Ponto único para ações após criação da mensagem.
    Futuramente pode disparar fila, webhook, CRM ou notificação.
    """

    send_new_contact_notification(message)
    return message


@transaction.atomic
def reply_to_contact_message(message, user, response_message, send_email=True):
    message.mark_as_responded(user=user, response_message=response_message)

    if send_email:
        send_contact_reply_email(message)

    return message