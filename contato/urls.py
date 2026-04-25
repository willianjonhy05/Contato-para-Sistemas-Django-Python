from django.urls import path

from .views import (
    ContactCreateView,
    ContactMessageArchiveView,
    ContactMessageDetailView,
    ContactMessageListView,
    ContactMessageReplyView,
    ContactMessageUpdateView,
    ContactNoteCreateView,
    ContactSuccessView,
)

app_name = "contacts"

urlpatterns = [
    path("contato/", ContactCreateView.as_view(), name="contact_create"),
    path("contato/enviado/", ContactSuccessView.as_view(), name="contact_success"),

    path(
        "contatos/painel/",
        ContactMessageListView.as_view(),
        name="staff_message_list",
    ),
    path(
        "contatos/painel/<uuid:slug>/",
        ContactMessageDetailView.as_view(),
        name="staff_message_detail",
    ),
    path(
        "contatos/painel/<uuid:slug>/editar/",
        ContactMessageUpdateView.as_view(),
        name="staff_message_update",
    ),
    path(
        "contatos/painel/<uuid:slug>/responder/",
        ContactMessageReplyView.as_view(),
        name="staff_message_reply",
    ),
    path(
        "contatos/painel/<uuid:slug>/arquivar/",
        ContactMessageArchiveView.as_view(),
        name="staff_message_archive",
    ),
    path(
        "contatos/painel/<uuid:slug>/anotacoes/nova/",
        ContactNoteCreateView.as_view(),
        name="staff_note_create",
    ),
]