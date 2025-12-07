import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from puceats.models import Token
from django.utils import timezone
from datetime import timedelta

# Criar token novo
token = Token.objects.create(expires_at=timezone.now() + timedelta(days=30))

print(f"\n✅ Token criado com sucesso!")
print(f"\n📋 Copie este código (SEM espaços):")
print(f"\n    {token.code}")
print(f"\n📅 Expira em: {token.expires_at.strftime('%d/%m/%Y às %H:%M')}")
print(f"\n💡 Use este código na tela de cadastro\n")
