import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from puceats.models import Token

print("=== Tokens no Banco de Dados ===\n")

tokens = Token.objects.all().order_by('-created_at')[:5]

if not tokens:
    print("❌ Nenhum token encontrado no banco!")
else:
    for token in tokens:
        print(f"Code: {token.code}")
        print(f"  Usado: {'Sim' if token.is_used else 'Não'}")
        print(f"  Usado por: {token.used_by if token.used_by else 'Ninguém'}")
        print(f"  Criado em: {token.created_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"  Expira em: {token.expires_at.strftime('%d/%m/%Y %H:%M')}")
        
        valido, mensagem = token.is_valid()
        print(f"  Status: {mensagem}")
        print()
