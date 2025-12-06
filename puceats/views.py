from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Token, Restaurant
import requests

def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        email_ou_username = request.POST.get('email')
        senha = request.POST.get('senha')
        
        # Tentar autenticar por username
        usuario = authenticate(request, username=email_ou_username, password=senha)
        
        # Se não funcionou, tentar por email
        if not usuario:
            try:
                user_obj = User.objects.get(email=email_ou_username)
                usuario = authenticate(request, username=user_obj.username, password=senha)
            except User.DoesNotExist:
                pass
        
        if usuario is not None:
            auth_login(request, usuario)
            messages.success(request, f'Bem-vindo, {usuario.username}!')
            return redirect('puceats:crud_restaurantes')
        else:
            messages.error(request, 'Email/Usuário ou senha incorretos.')
    
    return render(request, 'login.html')

def cadastro(request):
    if request.method == 'POST':
        token_code = request.POST.get('token')
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar')
        nome_restaurante = request.POST.get('nome_restaurante')
        
        # Validações básicas
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'cadastro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado.')
            return render(request, 'cadastro.html')
        
        # Validar token
        try:
            token = Token.objects.get(code=token_code.upper())
            valido, mensagem = token.is_valid()
            
            if not valido:
                messages.error(request, f'Token inválido: {mensagem}')
                return render(request, 'cadastro.html')
            
            # Criar usuário (usando email como username)
            usuario = User.objects.create_user(
                username=email,
                email=email,
                password=senha,
                first_name=nome
            )
            
            # Criar primeiro restaurante
            restaurante = Restaurant.objects.create(
                owner=usuario,
                name=nome_restaurante
            )
            
            # Marcar token como usado
            token.is_used = True
            token.used_by = usuario
            token.used_at = timezone.now()
            token.save()
            
            # Fazer login automático
            auth_login(request, usuario)
            messages.success(request, f'Conta criada com sucesso! Restaurante "{nome_restaurante}" cadastrado.')
            return redirect('puceats:crud_restaurantes')
            
        except Token.DoesNotExist:
            messages.error(request, 'Token não encontrado.')
            return render(request, 'cadastro.html')
    
    return render(request, 'cadastro.html')

def esqueci_senha(request):
    return render(request, 'EsqueciMinhaSenha.html')

def favoritos(request):
    return render(request, 'Favoritos.html')

def logout(request):
    """View para fazer logout do usuário"""
    auth_logout(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('puceats:index')

def crud(request):
    return render(request, 'crud.html')

def exemplo_consumir_api(request):
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
        data = response.json()
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

