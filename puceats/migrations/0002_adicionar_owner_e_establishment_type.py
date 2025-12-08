# Migration incremental - adiciona owner e establishment_type aos restaurantes existentes

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def atribuir_restaurantes_ao_superusuario(apps, schema_editor):
    """
    Pega o primeiro superusuário existente e atribui todos os restaurantes a ele.
    """
    Usuario = apps.get_model(settings.AUTH_USER_MODEL)
    Restaurante = apps.get_model('puceats', 'Restaurant')
    
    # Buscar qualquer superusuário existente
    superusuario = Usuario.objects.filter(is_superuser=True).first()
    
    if not superusuario:
        print("⚠ Nenhum superusuário encontrado. Crie um com: python manage.py createsuperuser")
        return
    
    # Atribuir todos os restaurantes existentes ao superusuário
    restaurantes = Restaurante.objects.filter(owner__isnull=True)
    quantidade = restaurantes.update(owner=superusuario)
    if quantidade > 0:
        print(f"✓ {quantidade} restaurante(s) atribuído(s) ao superusuário '{superusuario.username}'")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('puceats', '0001_initial'),
    ]

    operations = [
        # Criar model Token
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(editable=False, max_length=32, unique=True)),
                ('is_used', models.BooleanField(default=False, verbose_name='Já foi usado?')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('expires_at', models.DateTimeField(verbose_name='Expira em')),
                ('used_at', models.DateTimeField(blank=True, null=True, verbose_name='Usado em')),
                ('used_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tokens_used', to=settings.AUTH_USER_MODEL, verbose_name='Usado por')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
                'ordering': ['-created_at'],
            },
        ),
        
        # Adicionar campo owner no Restaurant
        migrations.AddField(
            model_name='restaurant',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restaurants', to=settings.AUTH_USER_MODEL, verbose_name='Proprietário'),
        ),
        
        # Adicionar campo establishment_type no Restaurant
        migrations.AddField(
            model_name='restaurant',
            name='establishment_type',
            field=models.CharField(choices=[('restaurante', 'Restaurante'), ('lanchonete', 'Lanchonete'), ('barraca', 'Barraca')], default='restaurante', max_length=20, verbose_name='Tipo de Estabelecimento'),
        ),
        
        # Atribuir restaurantes existentes ao superusuário
        migrations.RunPython(atribuir_restaurantes_ao_superusuario),
    ]
