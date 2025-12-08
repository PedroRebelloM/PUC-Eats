from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
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

def restaurantes_view(request):
    restaurantes = Restaurant.objects.filter(establishment_type='restaurante').prefetch_related('dishes')
    
    context = {
        'restaurants': restaurantes,
        'page_title': 'Restaurantes',
        'establishment_type': 'restaurante',
        'icon': 'restaurant',
    }
    return render(request, 'estabelecimentos.html', context)

def lanchonetes_view(request):
    lanchonetes = Restaurant.objects.filter(establishment_type='lanchonete').prefetch_related('dishes')
    
    context = {
        'restaurants': lanchonetes,
        'page_title': 'Lanchonetes',
        'establishment_type': 'lanchonete',
        'icon': 'lunch_dining',
    }
    return render(request, 'estabelecimentos.html', context)

def barracas_view(request):
    barracas = Restaurant.objects.filter(establishment_type='barraca').prefetch_related('dishes')
    
    context = {
        'restaurants': barracas,
        'page_title': 'Barracas',
        'establishment_type': 'barraca',
        'icon': 'storefront',
    }
    return render(request, 'estabelecimentos.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Restaurant, Dish, Category
import requests

def index(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'index.html', {"restaurants": restaurants})

def login(request):
    # Se já está logado, faz logout primeiro para evitar sessões antigas
    if request.user.is_authenticated:
        auth_logout(request)
    
    if request.method == 'POST':
        email_ou_username = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')
        
        if not email_ou_username or not senha:
            messages.error(request, 'Por favor, preencha seu email/usuário e senha para continuar.')
            return render(request, 'login.html')
        
        # Tenta autenticar por username
        usuario = authenticate(request, username=email_ou_username, password=senha)
        
        # Se não funcionou, tenta por email
        if not usuario:
            try:
                user_obj = User.objects.get(email=email_ou_username)
                usuario = authenticate(request, username=user_obj.username, password=senha)
            except User.DoesNotExist:
                pass
        
        if usuario is not None:
            # Faz logout de qualquer sessão anterior antes de logar
            auth_logout(request)
            # Agora faz login com o usuário correto
            auth_login(request, usuario)
            nome_exibir = usuario.first_name if usuario.first_name else usuario.username
            messages.success(request, f'Bem-vindo de volta, {nome_exibir}! Login realizado com sucesso.')
            return redirect('puceats:crud')
        else:
            messages.error(request, 'Credenciais inválidas. Verifique seu email/usuário e senha e tente novamente.')
    
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
            messages.error(request, 'As senhas não coincidem. Por favor, digite a mesma senha nos dois campos.')
            return render(request, 'cadastro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado. Faça login ou use outro email.')
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
            messages.success(request, f'🎉 Conta criada com sucesso! Bem-vindo ao PUC Eats, {nome}! Seu restaurante "{nome_restaurante}" foi cadastrado.')
            return redirect('puceats:crud')
            
        except Token.DoesNotExist:
            messages.error(request, 'Token não encontrado. Verifique se digitou corretamente ou entre em contato com o administrador.')
            return render(request, 'cadastro.html')
    
    return render(request, 'cadastro.html')

def esqueci_senha(request):
    return render(request, 'EsqueciMinhaSenha.html')

def favoritos(request):
    return render(request, 'Favoritos.html')

def logout(request):
    """View para fazer logout do usuário"""
    nome_exibir = ''
    if request.user.is_authenticated:
        nome_exibir = request.user.first_name if request.user.first_name else request.user.username
    auth_logout(request)
    if nome_exibir:
        messages.success(request, f'Até logo, {nome_exibir}! Volte sempre ao PUC Eats.')
    else:
        messages.success(request, 'Logout realizado com sucesso. Até breve!')
    return redirect('puceats:index')

@login_required(login_url='/puceats/login/')
def crud(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        categoria_nome = request.POST.get('categoria')
        preco = request.POST.get('preco')
        tipo_imagem = request.POST.get('tipoImagem')
        restaurant_id = request.POST.get('restaurant_id')
        dish_id = request.POST.get('dish_id')  # Para edição
        
        # Validações
        if not nome or not descricao or not preco or not restaurant_id:
            return JsonResponse({'success': False, 'error': 'Campos obrigatórios não preenchidos'})
        
        # Busca ou cria a categoria (se fornecida)
        categoria = None
        if categoria_nome and categoria_nome.strip():
            categoria, _ = Category.objects.get_or_create(name=categoria_nome)
        
        # Busca o restaurante específico do usuário logado
        try:
            restaurante = Restaurant.objects.get(id=restaurant_id, owner=request.user)
        except Restaurant.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Restaurante não encontrado ou você não tem permissão'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erro ao buscar restaurante: {str(e)}'})
        
        # Edita ou cria o prato
        if dish_id:
            try:
                prato = Dish.objects.get(id=dish_id, restaurant__owner=request.user)
                prato.name = nome
                prato.description = descricao
                prato.price = preco
                prato.category = categoria
                prato.restaurant = restaurante
            except Dish.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Prato não encontrado'})
        else:
            # Criação
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
            elif not dish_id:  # Se é criação e não tem URL, deixa None
                prato.image = None
        elif tipo_imagem == 'upload':
            imagem_arquivo = request.FILES.get('imagemArquivo')
            if imagem_arquivo:
                prato.image = imagem_arquivo
        elif tipo_imagem == 'nenhuma':
            prato.image = None
        
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
    
    # GET - Passa lista de restaurantes e pratos do restaurante selecionado
    # Debug: Verifica qual usuário está logado
    print(f"DEBUG: Usuário logado = {request.user.username} (ID: {request.user.id})")
    
    restaurantes = Restaurant.objects.filter(owner=request.user)
    print(f"DEBUG: Encontrados {restaurantes.count()} restaurantes para o usuário {request.user.username}")
    
    # Se tem um restaurant_id na query string, filtra os pratos
    selected_restaurant_id = request.GET.get('restaurant_id')
    pratos = []
    selected_restaurant = None
    
    if selected_restaurant_id:
        try:
            selected_restaurant = Restaurant.objects.get(id=selected_restaurant_id, owner=request.user)
            pratos = Dish.objects.filter(restaurant=selected_restaurant).select_related('category')
        except Restaurant.DoesNotExist:
            pass
    elif restaurantes.exists():
        selected_restaurant = restaurantes.first()
        pratos = Dish.objects.filter(restaurant=selected_restaurant).select_related('category')
    
    context = {
        'restaurants': restaurantes,
        'dishes': pratos,
        'selected_restaurant': selected_restaurant
    }
    return render(request, 'crud.html', context)

@login_required(login_url='/puceats/login/')
def delete_dish(request, dish_id):
    if request.method == 'POST':
        try:
            # Busca o prato e verifica se pertence a um restaurante do usuário
            prato = Dish.objects.get(id=dish_id, restaurant__owner=request.user)
            prato.delete()
            return JsonResponse({'success': True})
        except Dish.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Prato não encontrado ou você não tem permissão'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required(login_url='/puceats/login/')
def get_dish(request, dish_id):
    try:
        prato = Dish.objects.get(id=dish_id, restaurant__owner=request.user)
        return JsonResponse({
            'success': True,
            'dish': {
                'id': prato.id,
                'name': prato.name,
                'description': prato.description,
                'price': str(prato.price),
                'category': prato.category.name if prato.category else '',
                'restaurant_id': prato.restaurant.id,
                'image': prato.image.url if prato.image else None
            }
        })
    except Dish.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Prato não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/puceats/login/')
def add_restaurant(request):
    if request.method == 'POST':
        token_code = request.POST.get('token', '').strip()
        nome_restaurante = request.POST.get('nome_restaurante', '').strip()
        establishment_type = request.POST.get('establishment_type', '').strip()
        
        if not token_code or not nome_restaurante or not establishment_type:
            messages.error(request, 'Por favor, preencha todos os campos (token, nome do restaurante e tipo de estabelecimento).')
            return redirect('puceats:crud')
        
        try:
            # Valida o token
            token = Token.objects.get(code=token_code.upper())
            
            if not token.is_valid():
                messages.error(request, 'Token inválido ou expirado. Solicite um novo token ao administrador.')
                return redirect('puceats:crud')
            
            if token.is_used:
                messages.error(request, 'Este token já foi utilizado. Cada token pode ser usado apenas uma vez. Solicite um novo token.')
                return redirect('puceats:crud')
            
            # Cria o restaurante
            restaurante = Restaurant.objects.create(
                owner=request.user,
                name=nome_restaurante,
                establishment_type=establishment_type
            )
            
            # Marca o token como usado
            token.is_used = True
            token.used_by = request.user
            token.used_at = timezone.now()
            token.save()
            
            messages.success(request, f'Parabéns! Restaurante "{nome_restaurante}" criado com sucesso! Você já pode começar a adicionar pratos ao cardápio.')
            return redirect(f'/puceats/crud/?restaurant_id={restaurante.id}')
            
        except Token.DoesNotExist:
            messages.error(request, 'Token não encontrado. Verifique se digitou corretamente.')
            return redirect('puceats:crud')
        except Exception as e:
            messages.error(request, f'Ops! Ocorreu um erro ao criar o restaurante: {str(e)}. Tente novamente ou entre em contato com o suporte.')
            return redirect('puceats:crud')
    
    return redirect('puceats:crud')
    dishes = Dish.objects.all().select_related('restaurant', 'category')
    categories = Category.objects.all()
    restaurants = Restaurant.objects.all()
    
    return render(request, 'crud.html', {
        'dishes': dishes,
        'categories': categories,
        'restaurants': restaurants
    })

def crud_restaurantes(request):
    restaurants = Restaurant.objects.all().order_by('name')
    return render(request, 'crud_restaurantes.html', {
        'restaurants': restaurants
    })

def exemplo_consumir_api(request):
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
        data = response.json()
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/puceats/login/')
def admin_panel(request):
    """View do painel administrativo - apenas para superuser"""
    if not request.user.is_superuser:
        messages.error(request, '❌ Acesso negado. Apenas administradores podem acessar esta área.')
        return redirect('puceats:index')
    
    # Estatísticas gerais
    total_users = User.objects.count()
    total_restaurants = Restaurant.objects.count()
    total_dishes = Dish.objects.count()
    total_tokens = Token.objects.count()
    tokens_used = Token.objects.filter(is_used=True).count()
    tokens_available = total_tokens - tokens_used
    
    # Dados detalhados
    users = User.objects.all().order_by('-date_joined')
    restaurants = Restaurant.objects.all().select_related('owner').prefetch_related('dishes').order_by('-id')
    
    context = {
        'total_users': total_users,
        'total_restaurants': total_restaurants,
        'total_dishes': total_dishes,
        'total_tokens': total_tokens,
        'tokens_used': tokens_used,
        'tokens_available': tokens_available,
        'users': users,
        'restaurants': restaurants,
    }
    
    return render(request, 'admin.html', context)

def restaurant_detail(request, slug):
    """
    Página de detalhes de um restaurante.
    Busca pelo slug e mostra o cardápio.
    """
    restaurant = get_object_or_404(Restaurant, slug=slug)
    dishes = restaurant.dishes.all().select_related("category")

    return render(
        request,
        "restaurants/restaurant_detail.html",
        {
            "restaurant": restaurant,
            "dishes": dishes,
        },
    )

# === CRUD de Pratos ===
@require_http_methods(["POST"])
def dish_add(request):
    """Adicionar novo prato"""
    try:
        restaurant_id = request.POST.get('restaurant')
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        
        if not all([restaurant_id, name, price]):
            return JsonResponse({'success': False, 'error': 'Campos obrigatórios faltando'})
        
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        dish = Dish.objects.create(
            restaurant=restaurant,
            category_id=category_id if category_id else None,
            name=name,
            description=description,
            price=price,
            is_vegan=request.POST.get('is_vegan') == 'on',
            is_vegetarian=request.POST.get('is_vegetarian') == 'on',
            is_gluten_free=request.POST.get('is_gluten_free') == 'on',
        )
        
        if 'image' in request.FILES:
            dish.image = request.FILES['image']
            dish.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def dish_edit(request, dish_id):
    """Editar prato existente"""
    try:
        dish = get_object_or_404(Dish, id=dish_id)
        
        dish.name = request.POST.get('name', dish.name)
        dish.description = request.POST.get('description', dish.description)
        dish.price = request.POST.get('price', dish.price)
        
        category_id = request.POST.get('category')
        if category_id:
            dish.category_id = category_id
        
        restaurant_id = request.POST.get('restaurant')
        if restaurant_id:
            dish.restaurant_id = restaurant_id
        
        dish.is_vegan = request.POST.get('is_vegan') == 'on'
        dish.is_vegetarian = request.POST.get('is_vegetarian') == 'on'
        dish.is_gluten_free = request.POST.get('is_gluten_free') == 'on'
        
        if 'image' in request.FILES:
            dish.image = request.FILES['image']
        
        dish.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def dish_delete(request, dish_id):
    """Deletar prato"""
    try:
        dish = get_object_or_404(Dish, id=dish_id)
        dish.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# === CRUD de Restaurantes ===
@require_http_methods(["POST"])
def restaurant_add(request):
    """Adicionar novo restaurante"""
    try:
        name = request.POST.get('name')
        if not name:
            return JsonResponse({'success': False, 'error': 'Nome é obrigatório'})
        
        # Preparar dados
        data = {
            'name': name,
            'description': request.POST.get('description', ''),
            'cuisine_type': request.POST.get('cuisine_type', 'outros'),
            'building': request.POST.get('building', ''),
            'price_level': int(request.POST.get('price_level', 3)),
            'phone': request.POST.get('phone', ''),
            'opening_hours': request.POST.get('opening_hours', ''),
            'instagram': request.POST.get('instagram', ''),
            'website': request.POST.get('website', '')
        }
        
        # Campos opcionais numéricos
        latitude = request.POST.get('latitude')
        if latitude:
            data['latitude'] = float(latitude)
        
        longitude = request.POST.get('longitude')
        if longitude:
            data['longitude'] = float(longitude)
        
        restaurant = Restaurant.objects.create(**data)
        
        # Upload de logo
        if 'logo' in request.FILES:
            restaurant.logo = request.FILES['logo']
            restaurant.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def restaurant_edit(request, restaurant_id):
    """Editar restaurante existente"""
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        restaurant.name = request.POST.get('name', restaurant.name)
        restaurant.description = request.POST.get('description', restaurant.description)
        restaurant.cuisine_type = request.POST.get('cuisine_type', restaurant.cuisine_type)
        restaurant.building = request.POST.get('building', restaurant.building)
        restaurant.price_level = int(request.POST.get('price_level', restaurant.price_level))
        restaurant.phone = request.POST.get('phone', restaurant.phone)
        restaurant.opening_hours = request.POST.get('opening_hours', restaurant.opening_hours)
        restaurant.instagram = request.POST.get('instagram', restaurant.instagram)
        restaurant.website = request.POST.get('website', restaurant.website)
        
        # Campos opcionais numéricos
        latitude = request.POST.get('latitude')
        if latitude:
            restaurant.latitude = float(latitude)
        
        longitude = request.POST.get('longitude')
        if longitude:
            restaurant.longitude = float(longitude)
        
        # Upload de logo
        if 'logo' in request.FILES:
            restaurant.logo = request.FILES['logo']
        
        restaurant.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def restaurant_delete(request, restaurant_id):
    """Deletar restaurante"""
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        restaurant.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
