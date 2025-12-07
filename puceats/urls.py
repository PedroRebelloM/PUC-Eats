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
    path('crud/', views.crud, name='crud'),
    path('add-restaurant/', views.add_restaurant, name='add_restaurant'),
    path('dish/<int:dish_id>/delete/', views.delete_dish, name='delete_dish'),
    path('dish/<int:dish_id>/get/', views.get_dish, name='get_dish'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('exemplo-api/', views.exemplo_consumir_api, name='exemplo-api'),
]
