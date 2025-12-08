from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets


class Token(models.Model):
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
            # Gerar código alfanumérico sem caracteres especiais
            self.code = secrets.token_hex(16).upper()[:32]
        if not self.expires_at:
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

    ESTABLISHMENT_TYPES = [
        ("restaurante", "Restaurante"),
        ("lanchonete", "Lanchonete"),
        ("barraca", "Barraca"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="restaurants",
        null=True,
        blank=True,
        verbose_name="Proprietário"
    )

    name = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=120, unique=True, verbose_name="Nome")
    slug = models.SlugField(unique=True, blank=True)

    logo = models.ImageField(upload_to="restaurantes/logos/", blank=True, null=True, verbose_name="Logo")

    description = models.TextField(blank=True, help_text="Descrição curta do restaurante")
    cuisine_type = models.CharField(max_length=30, choices=CUISINE_TYPES, default="outros")
    establishment_type = models.CharField(
        max_length=20,
        choices=ESTABLISHMENT_TYPES,
        default="restaurante",
        verbose_name="Tipo de Estabelecimento"
    )
    description = models.TextField(blank=True, verbose_name="Descrição", help_text="Descrição curta do restaurante")
    cuisine_type = models.CharField(max_length=30, choices=CUISINE_TYPES, default="outros", verbose_name="Tipo de Cozinha")

    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    building = models.CharField(max_length=80, blank=True, verbose_name="Prédio", help_text="Ex: Frings, Pilotis, etc.")

    opening_hours = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Horário de Funcionamento",
        help_text="Ex: Seg–Sex 8h–22h"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    instagram = models.URLField(blank=True, verbose_name="Instagram")
    website = models.URLField(blank=True, verbose_name="Site")

    price_level = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Nível de Preço",
        help_text="1–5 (quanto mais alto, mais caro)"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        ordering = ["name"]
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="Nome")
    icon = models.CharField(max_length=80, blank=True, verbose_name="Ícone", help_text="Nome do ícone da sua UI (opcional)")

    class Meta:
        ordering = ["name"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name


class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="dishes", verbose_name="Restaurante")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")

    name = models.CharField(max_length=120, verbose_name="Nome")
    slug = models.SlugField(blank=True)

    description = models.TextField(blank=True, verbose_name="Descrição")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Preço")

    is_vegan = models.BooleanField(default=False, verbose_name="Vegano")
    is_vegetarian = models.BooleanField(default=False, verbose_name="Vegetariano")
    is_gluten_free = models.BooleanField(default=False, verbose_name="Sem Glúten")

    available = models.BooleanField(default=True, verbose_name="Disponível")
    image = models.ImageField(upload_to="pratos/", blank=True, null=True, verbose_name="Imagem")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        ordering = ["name"]
        verbose_name = "Prato"
        verbose_name_plural = "Pratos"

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

