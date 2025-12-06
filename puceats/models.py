from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets


class Token(models.Model):
    """
    Token para autorizar abertura de novos restaurantes.
    Cada token permite criar 1 restaurante.
    """
    code = models.CharField(max_length=32, unique=True, editable=False)
    is_used = models.BooleanField(default=False, verbose_name="Já foi usado?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    expires_at = models.DateTimeField(verbose_name="Expira em")
    used_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="tokens_used",
        verbose_name="Usado por"
    )
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Usado em")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    def __str__(self):
        status = "Usado" if self.is_used else "Disponível"
        return f"{self.code} - {status}"

    def save(self, *args, **kwargs):
        if not self.code:
            # Gera código único de 32 caracteres
            self.code = secrets.token_urlsafe(24)[:32].upper()
        if not self.expires_at:
            # Expira em 30 dias por padrão
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Verifica se o token pode ser usado"""
        if self.is_used:
            return False, "Token já foi utilizado"
        if timezone.now() > self.expires_at:
            return False, "Token expirado"
        return True, "Token válido"


class Restaurant(models.Model):
    CUISINE_TYPES = [
        ("brasileira", "Brasileira"),
        ("japonesa", "Japonesa"),
        ("italiana", "Italiana"),
        ("árabe", "Árabe"),
        ("vegana", "Vegana"),
        ("cafeteria", "Cafeteria"),
        ("lanches", "Lanches"),
        ("internacional", "Internacional"),
        ("outros", "Outros"),
    ]

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    logo = models.ImageField(upload_to="restaurantes/logos/", blank=True, null=True)

    description = models.TextField(blank=True, help_text="Descrição curta do restaurante")
    cuisine_type = models.CharField(max_length=30, choices=CUISINE_TYPES, default="outros")

    # Localização no campus
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    building = models.CharField(max_length=80, blank=True, help_text="Ex: Frings, Pilotis, etc.")

    # Informações de operação
    opening_hours = models.CharField(
        max_length=120,
        blank=True,
        help_text="Ex: Seg–Sex 8h–22h"
    )
    phone = models.CharField(max_length=20, blank=True)
    instagram = models.URLField(blank=True)
    website = models.URLField(blank=True)

    # Faixa de preço média (boa prática para apps de cardápio)
    price_level = models.PositiveSmallIntegerField(
        default=1,
        help_text="1–5 (quanto mais alto, mais caro)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Categoria de pratos (churrasco, japonês, massas, smoothies, etc).
    Útil para organizar o cardápio dentro de cada restaurante.
    """
    name = models.CharField(max_length=60, unique=True)
    icon = models.CharField(max_length=80, blank=True, help_text="Nome do ícone da sua UI (opcional)")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="dishes")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)

    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    is_vegan = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)

    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="pratos/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

