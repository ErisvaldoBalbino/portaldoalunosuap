"""
Configuração WSGI para o projeto Portal.

Expõe o callable WSGI como uma variável de módulo chamada ``application``.

Para mais informações sobre este arquivo, veja
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')

application = get_wsgi_application()
app = application
