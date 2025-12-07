from django.urls import path
from . import views

app_name = 'puceats'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('esqueci-senha/', views.esqueci_senha, name='esqueci-senha'),
    path('favoritos/', views.favoritos, name='favoritos'),
    path('crud/', views.crud, name='crud'),
    path('exemplo-api/', views.exemplo_consumir_api, name='exemplo-api'),
]
