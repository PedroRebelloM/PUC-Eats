"""
Script para criar tokens de autorização
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from puceats.models import Token
from django.utils import timezone
from datetime import timedelta

def criar_tokens(quantidade=5, dias_validade=30):
    """Cria múltiplos tokens"""
    print(f"=== Criando {quantidade} token(s) ===\n")
    
    tokens_criados = []
    
    for i in range(quantidade):
        token = Token.objects.create(
            expires_at=timezone.now() + timedelta(days=dias_validade)
        )
        tokens_criados.append(token)
        print(f"Token {i+1}: {token.code}")
        print(f"  - Expira em: {token.expires_at.strftime('%d/%m/%Y %H:%M')}")
        print()
    
    print(f"✅ {quantidade} token(s) criado(s) com sucesso!")
    print(f"📅 Validade: {dias_validade} dias")
    print("\n💡 Use esses códigos na tela de cadastro para criar novas contas de restaurante.")
    
    return tokens_criados

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        try:
            quantidade = int(sys.argv[1])
        except ValueError:
            print("❌ Quantidade deve ser um número inteiro")
            sys.exit(1)
    else:
        quantidade = 5
    
    if len(sys.argv) > 2:
        try:
            dias_validade = int(sys.argv[2])
        except ValueError:
            print("❌ Dias de validade deve ser um número inteiro")
            sys.exit(1)
    else:
        dias_validade = 30
    
    criar_tokens(quantidade, dias_validade)
