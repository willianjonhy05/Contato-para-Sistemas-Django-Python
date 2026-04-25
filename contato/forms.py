from django import forms

from .models import ContactMessage, ContactNote


class ContactMessageForm(forms.ModelForm):
    """
    Formulário público.
    Inclui honeypot simples contra bots.
    """

    website = forms.CharField(
        required=False,
        label="Website",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "class": "contact-hidden-field",
            }
        ),
    )

    class Meta:
        model = ContactMessage
        fields = [
            "category",
            "name",
            "email",
            "phone",
            "subject",
            "message",
            "terms_accepted",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
            "terms_accepted": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "category": "Setor",
            "name": "Nome",
            "email": "E-mail",
            "phone": "Telefone",
            "subject": "Assunto",
            "message": "Mensagem",
            "terms_accepted": "Li e aceito os termos de contato",
        }

    def clean_website(self):
        website = self.cleaned_data.get("website")
        if website:
            raise forms.ValidationError("Não foi possível enviar a mensagem.")
        return website

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()

        if len(message) < 10:
            raise forms.ValidationError("A mensagem precisa ter pelo menos 10 caracteres.")

        return message


class ContactMessageFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Busca",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nome, e-mail, assunto ou mensagem",
            }
        ),
    )

    status = forms.ChoiceField(
        required=False,
        label="Status",
        choices=[("", "Todos")] + list(ContactMessage.Status.choices),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    priority = forms.ChoiceField(
        required=False,
        label="Prioridade",
        choices=[("", "Todas")] + list(ContactMessage.Priority.choices),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_spam = forms.ChoiceField(
        required=False,
        label="Spam",
        choices=[
            ("", "Todos"),
            ("yes", "Somente spam"),
            ("no", "Não spam"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class ContactMessageAdminForm(forms.ModelForm):
    """
    Formulário interno para atualizar triagem da mensagem.
    """

    class Meta:
        model = ContactMessage
        fields = [
            "category",
            "status",
            "priority",
            "is_read",
            "is_spam",
            "assigned_to",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "assigned_to": forms.Select(attrs={"class": "form-control"}),
        }


class ContactReplyForm(forms.Form):
    response_message = forms.CharField(
        label="Resposta",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Digite a resposta que será enviada ao usuário.",
            }
        ),
    )
    send_email = forms.BooleanField(
        label="Enviar resposta por e-mail",
        required=False,
        initial=True,
    )


class ContactNoteForm(forms.ModelForm):
    class Meta:
        model = ContactNote
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Adicione uma anotação interna.",
                }
            )
        }
        labels = {
            "content": "Anotação interna",
        }