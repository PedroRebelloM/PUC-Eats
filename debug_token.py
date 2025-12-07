import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from puceats.models import Token

# Token que você tentou usar
token_teste = "WCZKJUUXZE4PLPUSU9PALSV1QBIZ_1XD"

print(f"=== Testando Token: {token_teste} ===\n")

# Buscar exatamente como está
try:
    token = Token.objects.get(code=token_teste)
    print(f"✓ Token encontrado EXATO!")
    print(f"  Code: {token.code}")
    print(f"  Usado: {token.is_used}")
    print(f"  Expira em: {token.expires_at}")
    valido, msg = token.is_valid()
    print(f"  Válido: {msg}")
except Token.DoesNotExist:
    print(f"✗ Token NÃO encontrado com código exato")

# Buscar sem underscore
token_sem_underscore = token_teste.replace('_', '').replace('-', '')
try:
    token = Token.objects.get(code=token_sem_underscore)
    print(f"\n✓ Token encontrado SEM underscore!")
    print(f"  Code: {token.code}")
except Token.DoesNotExist:
    print(f"\n✗ Token NÃO encontrado sem underscore")

# Listar TODOS os tokens
print(f"\n=== Todos os Tokens no Banco ===")
for t in Token.objects.all():
    print(f"  {t.code} - Usado: {t.is_used} - Expira: {t.expires_at}")
