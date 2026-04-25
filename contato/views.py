from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView, UpdateView, View

from .forms import (
    ContactMessageAdminForm,
    ContactMessageFilterForm,
    ContactMessageForm,
    ContactNoteForm,
    ContactReplyForm,
)
from .models import ContactMessage, ContactNote
from .services import register_new_contact_message, reply_to_contact_message
from .utils import get_client_ip, get_source_url, get_user_agent


class ContactCreateView(FormView):
    template_name = "contatos/public/contact_form.html"
    form_class = ContactMessageForm
    success_url = reverse_lazy("contacts:contact_success")

    def form_valid(self, form):
        contact_message = form.save(commit=False)
        contact_message.ip_address = get_client_ip(self.request)
        contact_message.user_agent = get_user_agent(self.request)
        contact_message.source_url = get_source_url(self.request)
        contact_message.save()

        register_new_contact_message(contact_message)

        messages.success(
            self.request,
            "Sua mensagem foi enviada com sucesso. Em breve entraremos em contato.",
        )

        return super().form_valid(form)


class ContactSuccessView(TemplateView):
    template_name = "contatos/public/contact_success.html"


class StaffPermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Exige usuário autenticado, staff ativo e permissão específica.
    """

    login_url = reverse_lazy("admin:login")
    raise_exception = True

    def has_permission(self):
        user = self.request.user

        if not user.is_authenticated:
            return False

        if not user.is_active or not user.is_staff:
            return False

        return super().has_permission()


class ContactMessageListView(StaffPermissionRequiredMixin, ListView):
    model = ContactMessage
    template_name = "contatos/staff/message_list.html"
    context_object_name = "contact_messages"
    paginate_by = 20
    permission_required = "contacts.view_contactmessage"

    def get_queryset(self):
        queryset = (
            ContactMessage.objects
            .select_related("category", "assigned_to", "responded_by")
            .order_by("-created_at")
        )

        self.filter_form = ContactMessageFilterForm(self.request.GET)

        if self.filter_form.is_valid():
            q = self.filter_form.cleaned_data.get("q")
            status = self.filter_form.cleaned_data.get("status")
            priority = self.filter_form.cleaned_data.get("priority")
            is_spam = self.filter_form.cleaned_data.get("is_spam")

            if q:
                queryset = queryset.filter(
                    Q(name__icontains=q)
                    | Q(email__icontains=q)
                    | Q(subject__icontains=q)
                    | Q(message__icontains=q)
                )

            if status:
                queryset = queryset.filter(status=status)

            if priority:
                queryset = queryset.filter(priority=priority)

            if is_spam == "yes":
                queryset = queryset.filter(is_spam=True)

            if is_spam == "no":
                queryset = queryset.filter(is_spam=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["filter_form"] = self.filter_form

        context["status_counts"] = (
            ContactMessage.objects
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

        context["unread_count"] = ContactMessage.objects.filter(is_read=False).count()

        return context


class ContactMessageDetailView(StaffPermissionRequiredMixin, DetailView):
    model = ContactMessage
    template_name = "contatos/staff/message_detail.html"
    context_object_name = "contact_message"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    permission_required = "contacts.view_contactmessage"

    def get_queryset(self):
        return (
            ContactMessage.objects
            .select_related("category", "assigned_to", "responded_by")
            .prefetch_related("notes")
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if not obj.is_read:
            obj.mark_as_read()

        return obj


class ContactMessageUpdateView(StaffPermissionRequiredMixin, UpdateView):
    model = ContactMessage
    form_class = ContactMessageAdminForm
    template_name = "contatos/staff/message_form.html"
    context_object_name = "contact_message"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    permission_required = "contacts.change_contactmessage"

    def get_success_url(self):
        return reverse(
            "contacts:staff_message_detail",
            kwargs={"slug": self.object.slug},
        )

    def form_valid(self, form):
        messages.success(self.request, "Mensagem atualizada com sucesso.")
        return super().form_valid(form)


class ContactMessageReplyView(StaffPermissionRequiredMixin, FormView):
    template_name = "contatos/staff/message_reply.html"
    form_class = ContactReplyForm
    permission_required = "contacts.reply_contactmessage"

    def dispatch(self, request, *args, **kwargs):
        self.contact_message = get_object_or_404(
            ContactMessage,
            slug=kwargs.get("slug"),
        )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()

        if self.contact_message.response_message:
            initial["response_message"] = self.contact_message.response_message

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_message"] = self.contact_message
        return context

    def form_valid(self, form):
        reply_to_contact_message(
            message=self.contact_message,
            user=self.request.user,
            response_message=form.cleaned_data["response_message"],
            send_email=form.cleaned_data["send_email"],
        )

        messages.success(self.request, "Resposta registrada com sucesso.")

        return redirect(
            "contacts:staff_message_detail",
            slug=self.contact_message.slug,
        )


class ContactMessageArchiveView(StaffPermissionRequiredMixin, View):
    permission_required = "contacts.archive_contactmessage"

    def post(self, request, *args, **kwargs):
        contact_message = get_object_or_404(
            ContactMessage,
            slug=kwargs.get("slug"),
        )
        contact_message.archive()

        messages.success(request, "Mensagem arquivada com sucesso.")

        return redirect("contacts:staff_message_list")


class ContactNoteCreateView(StaffPermissionRequiredMixin, FormView):
    template_name = "contatos/staff/note_form.html"
    form_class = ContactNoteForm
    permission_required = "contacts.change_contactmessage"

    def dispatch(self, request, *args, **kwargs):
        self.contact_message = get_object_or_404(
            ContactMessage,
            slug=kwargs.get("slug"),
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        note = form.save(commit=False)
        note.message = self.contact_message
        note.author = self.request.user
        note.save()

        messages.success(self.request, "Anotação interna adicionada com sucesso.")

        return redirect(
            "contacts:staff_message_detail",
            slug=self.contact_message.slug,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_message"] = self.contact_message
        return context