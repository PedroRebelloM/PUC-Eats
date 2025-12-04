from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Restaurant, Dish, Category
import requests

def index(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'index.html', {"restaurants": restaurants})

def login(request):
    return render(request, 'login.html')

def cadastro(request):
    return render(request, 'cadastro.html')

def esqueci_senha(request):
    return render(request, 'EsqueciMinhaSenha.html')

def favoritos(request):
    return render(request, 'Favoritos.html')

def crud(request):
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
