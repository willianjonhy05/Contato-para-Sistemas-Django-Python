def get_client_ip(request):
    """
    Captura o IP considerando proxy reverso.
    Em produção, configure corretamente SECURE_PROXY_SSL_HEADER
    e a infraestrutura de proxy.
    """

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")[:1000]


def get_source_url(request):
    return request.META.get("HTTP_REFERER", "")[:500]