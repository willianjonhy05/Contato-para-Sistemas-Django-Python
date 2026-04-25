# Contato para Sistemas Django Python

Aplicação reutilizável de contato desenvolvida em **Python** e **Django**, criada para adicionar uma funcionalidade profissional de **Fale Conosco** em diferentes projetos web.

O sistema permite que usuários enviem mensagens por meio de um formulário público, enquanto administradores podem visualizar, filtrar, responder, arquivar e organizar essas mensagens em uma área interna.

## Funcionalidades

- Formulário público de contato
- Uso de UUID como slug para URLs mais seguras
- Cadastro de categorias de contato
- Controle de status das mensagens
- Definição de prioridade
- Marcação de mensagens como lidas ou não lidas
- Identificação de mensagens como spam
- Atribuição de responsável pela mensagem
- Resposta ao usuário por e-mail
- Registro de resposta enviada
- Anotações internas para administradores
- Captura de IP, user agent e página de origem
- Integração com o Django Admin
- Permissões específicas para visualizar, editar, responder e arquivar mensagens
- Templates separados para área pública e área administrativa

## Tecnologias utilizadas

- Python
- Django
- HTML
- CSS
- SQLite, PostgreSQL ou outro banco compatível com Django
- Sistema nativo de autenticação e permissões do Django

## Estrutura principal do app

```txt
contacts/
├── admin.py
├── apps.py
├── emails.py
├── forms.py
├── models.py
├── services.py
├── urls.py
├── utils.py
├── views.py
└── templates/
    └── contacts/
        ├── public/
        │   ├── contact_form.html
        │   └── contact_success.html
        ├── staff/
        │   ├── message_list.html
        │   ├── message_detail.html
        │   ├── message_form.html
        │   ├── message_reply.html
        │   └── note_form.html
        └── emails/
            ├── new_contact_notification.txt
            └── contact_reply.txt