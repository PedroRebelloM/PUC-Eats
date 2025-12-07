from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Token, Restaurant, Dish, Category
import requests

def index(request):
    restaurantes = Restaurant.objects.all()
    pratos = Dish.objects.all()
    categorias = Category.objects.all()
    
    context = {
        'restaurants': restaurantes,
        'dishes': pratos,
        'categories': categorias,
    }
    return render(request, 'index.html', context)

def login(request):
    if request.method == 'POST':
        email_ou_username = request.POST.get('email')
        senha = request.POST.get('senha')
        
        usuario = authenticate(request, username=email_ou_username, password=senha)
        
        if not usuario:
            try:
                user_obj = User.objects.get(email=email_ou_username)
                usuario = authenticate(request, username=user_obj.username, password=senha)
            except User.DoesNotExist:
                pass
        
        if usuario is not None:
            auth_login(request, usuario)
            messages.success(request, f'Bem-vindo, {usuario.username}!')
            return redirect('puceats:crud')
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
        
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'cadastro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado.')
            return render(request, 'cadastro.html')
        
        try:
            token = Token.objects.get(code=token_code.upper())
            valido, mensagem = token.is_valid()
            
            if not valido:
                messages.error(request, f'Token inválido: {mensagem}')
                return render(request, 'cadastro.html')
            
            usuario = User.objects.create_user(
                username=email,
                email=email,
                password=senha,
                first_name=nome
            )
            
            restaurante = Restaurant.objects.create(
                owner=usuario,
                name=nome_restaurante
            )
            
            token.is_used = True
            token.used_by = usuario
            token.used_at = timezone.now()
            token.save()
            
            auth_login(request, usuario)
            messages.success(request, f'Conta criada com sucesso! Restaurante "{nome_restaurante}" cadastrado.')
            return redirect('puceats:crud')
            
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
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        categoria_nome = request.POST.get('categoria')
        preco = request.POST.get('preco')
        tipo_imagem = request.POST.get('tipoImagem')
        
        # Validações
        if not nome or not descricao or not preco:
            return JsonResponse({'success': False, 'error': 'Campos obrigatórios não preenchidos'})
        
        # Busca ou cria a categoria (se fornecida)
        categoria = None
        if categoria_nome and categoria_nome.strip():
            categoria, _ = Category.objects.get_or_create(name=categoria_nome)
        
        # Busca o restaurante do usuário logado
        try:
            restaurante = Restaurant.objects.filter(owner=request.user).first()
            if not restaurante:
                return JsonResponse({'success': False, 'error': 'Restaurante não encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erro ao buscar restaurante: {str(e)}'})
        
        # Cria o prato
        prato = Dish(
            restaurant=restaurante,
            category=categoria,
            name=nome,
            description=descricao,
            price=preco
        )
        
        # Processa a imagem conforme o tipo escolhido
        if tipo_imagem == 'url':
            imagem_url = request.POST.get('imagemUrl')
            if imagem_url:
                prato.image = imagem_url
        elif tipo_imagem == 'upload':
            imagem_arquivo = request.FILES.get('imagemArquivo')
            if imagem_arquivo:
                prato.image = imagem_arquivo
        # Se for 'nenhuma', não faz nada (image fica None/null)
        
        prato.save()
        
        return JsonResponse({
            'success': True,
            'dish': {
                'id': prato.id,
                'name': prato.name,
                'description': prato.description,
                'price': str(prato.price),
                'category': prato.category.name if prato.category else None,
                'image': prato.image.url if prato.image else None
            }
        })
    
    return render(request, 'crud.html')

def exemplo_consumir_api(request):
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
        data = response.json()
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

