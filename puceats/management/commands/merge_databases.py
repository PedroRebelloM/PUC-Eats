"""
Comando para fazer merge de dois bancos de dados SQLite.
Uso: python manage.py merge_databases db2.sqlite3
"""

from django.core.management.base import BaseCommand
from django.db import connection
import sqlite3
import os


class Command(BaseCommand):
    help = 'Faz merge de dados de outro banco SQLite para o banco atual'

    def add_arguments(self, parser):
        parser.add_argument(
            'source_db',
            type=str,
            help='Caminho para o banco de dados de origem (ex: db2.sqlite3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a operação sem fazer alterações'
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Pula a importação de usuários'
        )

    def handle(self, *args, **options):
        source_db = options['source_db']
        dry_run = options['dry_run']
        skip_users = options['skip_users']

        # Verifica se o arquivo existe
        if not os.path.exists(source_db):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {source_db}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Iniciando merge de {source_db}...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita'))

        # Conectar ao banco de origem
        source_conn = sqlite3.connect(source_db)
        source_cursor = source_conn.cursor()

        try:
            # 1. Importar Tokens
            self.stdout.write('\n--- TOKENS ---')
            self._merge_tokens(source_cursor, dry_run)

            # 2. Importar Usuários (se não for pulado)
            if not skip_users:
                self.stdout.write('\n--- USUÁRIOS ---')
                self._merge_users(source_cursor, dry_run)

            # 3. Importar Restaurantes
            self.stdout.write('\n--- RESTAURANTES ---')
            self._merge_restaurants(source_cursor, dry_run)

            # 4. Importar Categorias
            self.stdout.write('\n--- CATEGORIAS ---')
            self._merge_categories(source_cursor, dry_run)

            # 5. Importar Pratos
            self.stdout.write('\n--- PRATOS ---')
            self._merge_dishes(source_cursor, dry_run)

            if not dry_run:
                self.stdout.write(self.style.SUCCESS('\n✓ Merge concluído com sucesso!'))
            else:
                self.stdout.write(self.style.WARNING('\n✓ Simulação concluída. Use sem --dry-run para aplicar as alterações.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Erro durante o merge: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
        finally:
            source_conn.close()

    def _merge_tokens(self, source_cursor, dry_run):
        """Importa tokens do banco de origem"""
        source_cursor.execute("""
            SELECT code, is_used, created_at, expires_at, used_by_id, used_at
            FROM puceats_token
        """)
        
        tokens = source_cursor.fetchall()
        imported = 0
        skipped = 0

        for token in tokens:
            code = token[0]
            
            # Verifica se já existe
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM puceats_token WHERE code = %s", [code])
                exists = cursor.fetchone()

            if exists:
                skipped += 1
                continue

            if not dry_run:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO puceats_token 
                        (code, is_used, created_at, expires_at, used_by_id, used_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, token)
            
            imported += 1

        self.stdout.write(f'  Importados: {imported}')
        self.stdout.write(f'  Ignorados (duplicados): {skipped}')

    def _merge_users(self, source_cursor, dry_run):
        """Importa usuários do banco de origem"""
        source_cursor.execute("""
            SELECT username, first_name, last_name, email, password, 
                   is_superuser, is_staff, is_active, date_joined, last_login
            FROM auth_user
        """)
        
        users = source_cursor.fetchall()
        imported = 0
        skipped = 0

        for user in users:
            username = user[0]
            
            # Verifica se já existe
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM auth_user WHERE username = %s", [username])
                exists = cursor.fetchone()

            if exists:
                skipped += 1
                continue

            if not dry_run:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO auth_user 
                        (username, first_name, last_name, email, password, 
                         is_superuser, is_staff, is_active, date_joined, last_login)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, user)
            
            imported += 1

        self.stdout.write(f'  Importados: {imported}')
        self.stdout.write(f'  Ignorados (duplicados): {skipped}')

    def _merge_restaurants(self, source_cursor, dry_run):
        """Importa restaurantes do banco de origem"""
        source_cursor.execute("""
            SELECT name, slug, logo, description, cuisine_type, establishment_type,
                   latitude, longitude, building, opening_hours, phone, instagram,
                   website, price_level, created_at, owner_id
            FROM puceats_restaurant
        """)
        
        restaurants = source_cursor.fetchall()
        imported = 0
        skipped = 0

        for restaurant in restaurants:
            name = restaurant[0]
            
            # Verifica se já existe
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM puceats_restaurant WHERE name = %s", [name])
                exists = cursor.fetchone()

            if exists:
                self.stdout.write(self.style.WARNING(f'  Ignorando restaurante duplicado: {name}'))
                skipped += 1
                continue

            if not dry_run:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO puceats_restaurant 
                        (name, slug, logo, description, cuisine_type, establishment_type,
                         latitude, longitude, building, opening_hours, phone, instagram,
                         website, price_level, created_at, owner_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, restaurant)
            
            imported += 1
            self.stdout.write(f'  ✓ {name}')

        self.stdout.write(f'  Importados: {imported}')
        self.stdout.write(f'  Ignorados (duplicados): {skipped}')

    def _merge_categories(self, source_cursor, dry_run):
        """Importa categorias do banco de origem"""
        source_cursor.execute("""
            SELECT name, icon
            FROM puceats_category
        """)
        
        categories = source_cursor.fetchall()
        imported = 0
        skipped = 0

        for category in categories:
            name = category[0]
            
            # Verifica se já existe
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM puceats_category WHERE name = %s", [name])
                exists = cursor.fetchone()

            if exists:
                skipped += 1
                continue

            if not dry_run:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO puceats_category (name, icon)
                        VALUES (%s, %s)
                    """, category)
            
            imported += 1

        self.stdout.write(f'  Importados: {imported}')
        self.stdout.write(f'  Ignorados (duplicados): {skipped}')

    def _merge_dishes(self, source_cursor, dry_run):
        """Importa pratos do banco de origem"""
        from django.utils.text import slugify
        
        # Primeiro, precisamos mapear os IDs dos restaurantes e categorias
        restaurant_map = self._build_restaurant_map(source_cursor)
        category_map = self._build_category_map(source_cursor)

        source_cursor.execute("""
            SELECT name, description, price, image, is_vegan, is_vegetarian,
                   is_gluten_free, restaurant_id, category_id, available
            FROM puceats_dish
        """)
        
        dishes = source_cursor.fetchall()
        imported = 0
        skipped = 0

        for dish in dishes:
            name = dish[0]
            restaurant_id_old = dish[7]
            category_id_old = dish[8]
            available = dish[9] if len(dish) > 9 else True  # Default to True if not present

            # Mapeia os IDs antigos para os novos
            restaurant_id_new = restaurant_map.get(restaurant_id_old)
            category_id_new = category_map.get(category_id_old) if category_id_old else None

            if not restaurant_id_new:
                self.stdout.write(self.style.WARNING(f'  Ignorando prato sem restaurante: {name}'))
                skipped += 1
                continue

            # Verifica se já existe (mesmo nome no mesmo restaurante)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM puceats_dish WHERE name = %s AND restaurant_id = %s",
                    [name, restaurant_id_new]
                )
                exists = cursor.fetchone()

            if exists:
                skipped += 1
                continue

            if not dry_run:
                # Gerar slug único para o prato
                base_slug = slugify(name)
                slug = base_slug
                counter = 1
                
                # Garantir que o slug seja único
                while True:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT id FROM puceats_dish WHERE slug = %s", [slug])
                        if not cursor.fetchone():
                            break
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                from django.utils import timezone
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO puceats_dish 
                        (name, slug, description, price, image, is_vegan, is_vegetarian,
                         is_gluten_free, restaurant_id, category_id, available, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (dish[0], slug, dish[1], dish[2], dish[3], dish[4], dish[5],
                          dish[6], restaurant_id_new, category_id_new, available, timezone.now()))
            
            imported += 1

        self.stdout.write(f'  Importados: {imported}')
        self.stdout.write(f'  Ignorados (duplicados ou sem restaurante): {skipped}')

    def _build_restaurant_map(self, source_cursor):
        """Cria mapeamento de IDs de restaurantes (antigo -> novo)"""
        source_cursor.execute("SELECT id, name FROM puceats_restaurant")
        source_restaurants = source_cursor.fetchall()
        
        restaurant_map = {}
        for old_id, name in source_restaurants:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM puceats_restaurant WHERE name = %s", [name])
                result = cursor.fetchone()
                if result:
                    restaurant_map[old_id] = result[0]
        
        return restaurant_map

    def _build_category_map(self, source_cursor):
        """Cria mapeamento de IDs de categorias (antigo -> novo)"""
        source_cursor.execute("SELECT id, name FROM puceats_category")
        source_categories = source_cursor.fetchall()
        
        category_map = {}
        for old_id, name in source_categories:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM puceats_category WHERE name = %s", [name])
                result = cursor.fetchone()
                if result:
                    category_map[old_id] = result[0]
        
        return category_map
