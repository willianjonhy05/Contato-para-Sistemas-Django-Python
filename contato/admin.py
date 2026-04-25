from django.contrib import admin
from django.utils import timezone

from .models import ContactCategory, ContactMessage, ContactNote


@admin.register(ContactCategory)
class ContactCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "email_to", "is_active", "ordering"]
    list_filter = ["is_active"]
    search_fields = ["name", "description", "email_to"]
    readonly_fields = ["slug", "created_at", "updated_at"]
    ordering = ["ordering", "name"]


class ContactNoteInline(admin.TabularInline):
    model = ContactNote
    extra = 0
    readonly_fields = ["slug", "author", "created_at"]


@admin.action(description="Marcar como lidas")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True, updated_at=timezone.now())


@admin.action(description="Marcar como spam")
def mark_as_spam(modeladmin, request, queryset):
    queryset.update(is_spam=True, updated_at=timezone.now())


@admin.action(description="Arquivar selecionadas")
def archive_messages(modeladmin, request, queryset):
    queryset.update(
        status=ContactMessage.Status.ARCHIVED,
        archived_at=timezone.now(),
        updated_at=timezone.now(),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "name",
        "email",
        "category",
        "status",
        "priority",
        "is_read",
        "is_spam",
        "created_at",
    ]
    list_filter = [
        "status",
        "priority",
        "is_read",
        "is_spam",
        "category",
        "created_at",
    ]
    search_fields = [
        "name",
        "email",
        "phone",
        "subject",
        "message",
    ]
    readonly_fields = [
        "slug",
        "source_url",
        "ip_address",
        "user_agent",
        "created_at",
        "updated_at",
        "responded_at",
        "archived_at",
    ]
    date_hierarchy = "created_at"
    inlines = [ContactNoteInline]
    actions = [mark_as_read, mark_as_spam, archive_messages]

    fieldsets = (
        ("Dados do contato", {
            "fields": (
                "slug",
                "category",
                "name",
                "email",
                "phone",
                "subject",
                "message",
            )
        }),
        ("Triagem", {
            "fields": (
                "status",
                "priority",
                "is_read",
                "is_spam",
                "assigned_to",
            )
        }),
        ("Resposta", {
            "fields": (
                "response_message",
                "responded_by",
                "responded_at",
            )
        }),
        ("Dados técnicos", {
            "classes": ("collapse",),
            "fields": (
                "source_url",
                "ip_address",
                "user_agent",
                "terms_accepted",
            )
        }),
        ("Datas", {
            "fields": (
                "created_at",
                "updated_at",
                "archived_at",
            )
        }),
    )


@admin.register(ContactNote)
class ContactNoteAdmin(admin.ModelAdmin):
    list_display = ["message", "author", "created_at"]
    search_fields = ["message__subject", "content", "author__username"]
    readonly_fields = ["slug", "created_at"]