from django.urls import path
from . import views

app_name = 'puceats'

urlpatterns = [
    path('', views.index, name='index'),
    path('restaurantes/', views.restaurantes_view, name='restaurantes'),
    path('lanchonetes/', views.lanchonetes_view, name='lanchonetes'),
    path('barracas/', views.barracas_view, name='barracas'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('esqueci-senha/', views.esqueci_senha, name='esqueci-senha'),
    path('favoritos/', views.favoritos, name='favoritos'),
    
    # CRUD Pratos
    path('crud/', views.crud, name='crud'),
    path('add-restaurant/', views.add_restaurant, name='add_restaurant'),
    path('dish/<int:dish_id>/delete/', views.delete_dish, name='delete_dish'),
    path('dish/<int:dish_id>/get/', views.get_dish, name='get_dish'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('crud/dish/add/', views.dish_add, name='dish-add'),
    path('crud/dish/<int:dish_id>/edit/', views.dish_edit, name='dish-edit'),
    path('crud/dish/<int:dish_id>/delete/', views.dish_delete, name='dish-delete'),
    
    # CRUD Restaurantes
    path('crud/restaurantes/', views.crud_restaurantes, name='crud-restaurantes'),
    path('crud/restaurant/add/', views.restaurant_add, name='restaurant-add'),
    path('crud/restaurant/<int:restaurant_id>/edit/', views.restaurant_edit, name='restaurant-edit'),
    path('crud/restaurant/<int:restaurant_id>/delete/', views.restaurant_delete, name='restaurant-delete'),
    
    path('exemplo-api/', views.exemplo_consumir_api, name='exemplo-api'),
]
