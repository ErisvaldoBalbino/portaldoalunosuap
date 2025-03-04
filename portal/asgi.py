"""
Configuração ASGI para o projeto Portal.

Expõe o callable ASGI como uma variável de módulo chamada ``application``.

Para mais informações sobre este arquivo, veja
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')

application = get_asgi_application()
