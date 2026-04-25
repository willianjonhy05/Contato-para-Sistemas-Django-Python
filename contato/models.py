import uuid
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r"^\+?[\d\s\-\(\)]{8,20}$",
    message="Informe um telefone válido.",
)


class ContactCategory(models.Model):
    """
    Categoria ou setor responsável pela mensagem.
    Exemplo: Comercial, Suporte, Secretaria, Ouvidoria.
    """

    slug = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )
    name = models.CharField("Nome", max_length=100, unique=True)
    description = models.TextField("Descrição", blank=True)
    email_to = models.EmailField(
        "E-mail responsável",
        blank=True,
        help_text="Se preenchido, pode receber notificações dessa categoria.",
    )
    is_active = models.BooleanField("Ativa?", default=True)
    ordering = models.PositiveIntegerField("Ordem", default=0)

    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Categoria de contato"
        verbose_name_plural = "Categorias de contato"
        ordering = ["ordering", "name"]

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Nova"
        IN_PROGRESS = "in_progress", "Em atendimento"
        RESPONDED = "responded", "Respondida"
        CLOSED = "closed", "Finalizada"
        ARCHIVED = "archived", "Arquivada"

    class Priority(models.TextChoices):
        LOW = "low", "Baixa"
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        URGENT = "urgent", "Urgente"

    slug = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )

    category = models.ForeignKey(
        ContactCategory,
        verbose_name="Categoria",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )

    name = models.CharField("Nome", max_length=150)
    email = models.EmailField("E-mail")
    phone = models.CharField(
        "Telefone",
        max_length=20,
        blank=True,
        validators=[phone_validator],
    )
    subject = models.CharField("Assunto", max_length=180)
    message = models.TextField("Mensagem")

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    priority = models.CharField(
        "Prioridade",
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
    )

    is_read = models.BooleanField("Lida?", default=False)
    is_spam = models.BooleanField("Spam?", default=False)
    terms_accepted = models.BooleanField("Termos aceitos?", default=False)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Responsável",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_contact_messages",
    )

    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Respondida por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responded_contact_messages",
    )

    response_message = models.TextField("Resposta enviada", blank=True)
    responded_at = models.DateTimeField("Respondida em", null=True, blank=True)

    source_url = models.URLField("Página de origem", blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.TextField("User agent", blank=True)

    created_at = models.DateTimeField("Criada em", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Atualizada em", auto_now=True)
    archived_at = models.DateTimeField("Arquivada em", null=True, blank=True)

    class Meta:
        verbose_name = "Mensagem de contato"
        verbose_name_plural = "Mensagens de contato"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["priority", "created_at"]),
            models.Index(fields=["email"]),
        ]
        permissions = [
            ("reply_contactmessage", "Pode responder mensagem de contato"),
            ("archive_contactmessage", "Pode arquivar mensagem de contato"),
        ]

    def __str__(self):
        return f"{self.subject} - {self.name}"

    def get_absolute_url(self):
        return reverse("contacts:staff_message_detail", kwargs={"slug": self.slug})

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read", "updated_at"])

    def mark_as_in_progress(self, user=None):
        self.status = self.Status.IN_PROGRESS
        if user and not self.assigned_to:
            self.assigned_to = user
        self.save(update_fields=["status", "assigned_to", "updated_at"])

    def mark_as_responded(self, user, response_message):
        self.status = self.Status.RESPONDED
        self.is_read = True
        self.responded_by = user
        self.response_message = response_message
        self.responded_at = timezone.now()
        self.save(
            update_fields=[
                "status",
                "is_read",
                "responded_by",
                "response_message",
                "responded_at",
                "updated_at",
            ]
        )

    def archive(self):
        self.status = self.Status.ARCHIVED
        self.archived_at = timezone.now()
        self.save(update_fields=["status", "archived_at", "updated_at"])


class ContactNote(models.Model):
    """
    Anotações internas dos administradores.
    Não são exibidas ao usuário que enviou a mensagem.
    """

    slug = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )
    message = models.ForeignKey(
        ContactMessage,
        verbose_name="Mensagem",
        on_delete=models.CASCADE,
        related_name="notes",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Autor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_notes",
    )
    content = models.TextField("Anotação")
    created_at = models.DateTimeField("Criada em", auto_now_add=True)

    class Meta:
        verbose_name = "Anotação interna"
        verbose_name_plural = "Anotações internas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Nota de {self.author} em {self.created_at:%d/%m/%Y}"