# users/management/commands/seed_db.py
import random
from decimal import Decimal, ROUND_HALF_UP
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from faker import Faker

# Importamos todos los modelos necesarios
from users.models import User
from tenants.models import Tenant
from inventory.models import RawMaterial, PurchaseBatch
from products.models import Product, RecipeIngredient
from production.models import ProductionLog
from finance.models import Income, Expense

# Importamos nuestro servicio de producción para reutilizar la lógica de negocio
from production.services import register_production_batch

# Helpers
def qd(value):
    """Cuadra Decimal a 2 decimales con rounding consistente"""
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class Command(BaseCommand):
    help = 'Seeds the database with realistic, theme-consistent sample data for all models.'

    def add_arguments(self, parser):
        parser.add_argument('--seed', type=int, default=42, help='Random seed for Faker and random module')
        parser.add_argument('--production-plan', type=str, default='silla:10,sofa:3',
                            help="Plan de producción en formato 'slug:cantidad,slug2:cantidad' (ej: 'silla:10,sofa:3')")

    @transaction.atomic
    def handle(self, *args, **options):
        seed = options.get('seed', 42)
        random.seed(seed)
        Faker.seed(seed)
        faker = Faker('es_ES')

        self.stdout.write(self.style.NOTICE(f'Using seed={seed}'))

        # --- LIMPIEZA ordenada ---
        self.stdout.write('Deleting existing data (ordered deletions)...')
        ProductionLog.objects.all().delete()
        PurchaseBatch.objects.all().delete()
        RecipeIngredient.objects.all().delete()
        Product.objects.all().delete()
        RawMaterial.objects.all().delete()
        Income.objects.all().delete()
        Expense.objects.all().delete()
        User.objects.all().delete()
        Tenant.objects.all().delete()

        # --- 1. Crear Tenant y Usuario Principal ---
        self.stdout.write('Creating Tenant and main User...')
        tenant = Tenant.objects.create(name='Taller Creativo S.L.')
        admin_user = User.objects.create(
            tenant=tenant,
            email='productor@ejemplo.com',
            password=make_password('password123'),
            first_name='Juan',
            last_name='Productor',
            is_staff=True,
            is_superuser=True
        )

        # --- 2. Crear Materias Primas con descripciones coherentes ---
        self.stdout.write('Seeding Raw Materials (consistent names and units)...')
        raw_materials_def = [
            {'key': 'roble', 'name': 'Madera de Roble', 'unit': 'm²'},
            {'key': 'pino', 'name': 'Madera de Pino', 'unit': 'm²'},
            {'key': 'tornillo', 'name': 'Tornillo 1 pulgada', 'unit': 'unidad'},
            {'key': 'barniz', 'name': 'Barniz para madera', 'unit': 'litro'},
            {'key': 'lino', 'name': 'Tela de Lino', 'unit': 'metro'},
            {'key': 'espuma', 'name': 'Relleno de Espuma', 'unit': 'kg'},
        ]

        # Plantillas de descripción por key (puedes ampliar)
        raw_desc_templates = {
            'roble': [
                "Madera de roble de alta densidad, ideal para muebles y estructuras resistentes.",
                "Roble seleccionado, secado y cepillado, para acabados finos en carpintería."
            ],
            'pino': [
                "Madera de pino tratada, adecuada para estructuras interiores y encolado.",
                "Pino de crecimiento controlado, buena relación calidad/precio para marcos."
            ],
            'tornillo': [
                "Tornillo galvanizado 1 pulgada, uso general en ensamblaje de mobiliario.",
                "Tornillo de cabeza plana, resistente a la corrosión para uso en interiores."
            ],
            'barniz': [
                "Barniz acrílico para madera, acabado satinado, apto para interiores.",
                "Barniz protector de secado rápido, resistente a manchas y rayones."
            ],
            'lino': [
                "Tela de lino natural, gramaje medio, excelente para tapicería y acabados.",
                "Lino lavado, textura suave, ideal para tapizados y cojines."
            ],
            'espuma': [
                "Espuma de poliuretano de densidad media, cómoda para relleno de asientos.",
                "Relleno de espuma con buena recuperación, apto para sofás y colchonería."
            ]
        }

        raw_by_key = {}
        # creamos uno por uno para poder setear la descripción temática
        for r in raw_materials_def:
            desc_list = raw_desc_templates.get(r['key'], [faker.sentence(nb_words=8)])
            description = random.choice(desc_list)
            rm = RawMaterial.objects.create(
                tenant=tenant,
                name=r['name'],
                unit_of_measure=r['unit'],
                description=description
            )
            raw_by_key[r['key']] = rm

        # --- 3. Crear Productos y sus Recetas ---
        self.stdout.write('Seeding Products and their Recipes (fixed recipes)...')
        products_def = [
            {
                'slug': 'silla',
                'name': 'Silla de Roble Clásica',
                'category': 'Mueblería',
                'description': 'Una silla robusta y elegante para comedor.',
                'sale_price': Decimal('120.50'),
                'recipe': {
                    'roble': Decimal('2.5'),
                    'tornillo': Decimal('12'),
                    'barniz': Decimal('0.25'),
                }
            },
            {
                'slug': 'sofa',
                'name': 'Sofá de Lino Moderno',
                'category': 'Tapicería',
                'description': 'Un sofá cómodo para tres personas.',
                'sale_price': Decimal('750.00'),
                'recipe': {
                    'pino': Decimal('8.0'),
                    'lino': Decimal('10.0'),
                    'espuma': Decimal('15.0'),
                }
            }
        ]

        products = {}
        for pdef in products_def:
            p = Product.objects.create(
                tenant=tenant,
                name=pdef['name'],
                category=pdef['category'],
                description=pdef['description'],
                sale_price=qd(pdef['sale_price'])
            )
            products[pdef['slug']] = p
            ri_objs = []
            for rk, qty in pdef['recipe'].items():
                ri_objs.append(RecipeIngredient(
                    product=p,
                    raw_material=raw_by_key[rk],
                    quantity=qd(qty)
                ))
            RecipeIngredient.objects.bulk_create(ri_objs)

        # --- 4. Parse plan de producción ---
        plan_raw = {}
        plan_input = options.get('production-plan') or 'silla:10,sofa:3'
        if isinstance(plan_input, str):
            parts = [x.strip() for x in plan_input.split(',') if x.strip()]
            for part in parts:
                try:
                    slug, cantidad = part.split(':')
                    plan_raw[slug.strip()] = int(cantidad.strip())
                except Exception:
                    self.stdout.write(self.style.WARNING(f'Could not parse plan part "{part}", ignoring.'))
        if not plan_raw:
            plan_raw = {'silla': 10, 'sofa': 3}
        self.stdout.write(self.style.NOTICE(f'Production plan: {plan_raw}'))

        # --- 5. Calcular materiales necesarios y crear PurchaseBatches ---
        self.stdout.write('Calculating required raw material totals and seeding PurchaseBatches...')
        required_by_rm = {}
        for slug, qty_to_make in plan_raw.items():
            product = products.get(slug)
            if not product:
                continue
            ingredients = RecipeIngredient.objects.filter(product=product)
            for ing in ingredients:
                key = ing.raw_material.id
                need = (ing.quantity * Decimal(qty_to_make))
                required_by_rm.setdefault(key, Decimal('0.00'))
                required_by_rm[key] += need

        for rm_id, total_needed in required_by_rm.items():
            rm = RawMaterial.objects.get(id=rm_id)
            total_needed_with_buffer = (total_needed * Decimal('1.3')).quantize(Decimal('0.01'))
            remaining = total_needed_with_buffer
            lot_count = 1 if remaining <= Decimal('200') else random.randint(1, 2)
            for i in range(lot_count):
                if i == lot_count - 1:
                    qty = remaining
                else:
                    portion = float(remaining) * random.uniform(0.4, 0.7)
                    qty = Decimal(portion).quantize(Decimal('0.01'))
                    remaining = remaining - qty

                # heurística para unit_price (solo para calcular total)
                if 'madera' in rm.name.lower():
                    unit_price = Decimal(random.uniform(10.0, 25.0)).quantize(Decimal('0.01'))
                elif 'tornillo' in rm.name.lower():
                    unit_price = Decimal(random.uniform(0.05, 0.5)).quantize(Decimal('0.01'))
                elif 'barniz' in rm.name.lower():
                    unit_price = Decimal(random.uniform(5.0, 15.0)).quantize(Decimal('0.01'))
                elif 'tela' in rm.name.lower():
                    unit_price = Decimal(random.uniform(3.0, 12.0)).quantize(Decimal('0.01'))
                else:
                    unit_price = Decimal(random.uniform(1.0, 20.0)).quantize(Decimal('0.01'))

                total_cost = qd(qty * unit_price)

                try:
                    PurchaseBatch.objects.create(
                        tenant=tenant,
                        raw_material=rm,
                        purchase_date=faker.date_this_year(),
                        quantity=qd(qty),
                        total_cost=total_cost
                    )
                except TypeError as te:
                    self.stdout.write(self.style.WARNING(
                        f'PurchaseBatch create failed with TypeError: {te}. '
                        f'Attempting a fallback with minimal fields.'
                    ))
                    try:
                        PurchaseBatch.objects.create(
                            tenant=tenant,
                            raw_material=rm,
                            purchase_date=faker.date_this_year(),
                            quantity=qd(qty)
                        )
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Fallback also failed: {e} -- skipping this batch.'))

        # --- 6. Registrar lotes de producción vía servicio (fallback si falla) ---
        self.stdout.write('Seeding Production Logs by using the service...')
        for slug, qty in plan_raw.items():
            product = products.get(slug)
            if not product:
                self.stdout.write(self.style.WARNING(f'Product slug "{slug}" not found, skipping production.'))
                continue
            try:
                register_production_batch(user=admin_user, product_id=product.id, quantity_to_produce=qd(qty))
                self.stdout.write(self.style.SUCCESS(f'Registered production for {slug} x{qty} via service.'))
            except Exception as e:
                ProductionLog.objects.create(
                    tenant=tenant,
                    product=product,
                    quantity=qd(qty),
                    produced_by=admin_user,
                    produced_at=timezone.now(),
                    note=f'Fallback seed production record due to error: {str(e)}'
                )
                self.stdout.write(self.style.WARNING(f'Fallback production log for {slug} x{qty} created. Reason: {e}'))

        # --- 7. Crear Ingresos y Gastos con descripciones coherentes ---
        self.stdout.write('Seeding Incomes and Expenses (theme-consistent descriptions)...')
        products_list = list(products.values())
        batches = list(PurchaseBatch.objects.filter(tenant=tenant))

        # Ingresos: ventas simuladas por producto
        incomes = []
        for _ in range(8):
            product = random.choice(products_list)
            qty_sold = random.randint(1, 5)
            subtotal = qd(product.sale_price * Decimal(qty_sold))
            # aplicar variación por descuentos/comisiones
            multiplier = Decimal(str(random.uniform(0.95, 1.05)))
            amount = qd(subtotal * multiplier)
            description = f"Venta de {product.name} x{qty_sold} — orden {faker.bothify('ORD-####')} — {faker.company()}"
            incomes.append(Income(
                tenant=tenant,
                description=description,
                amount=amount,
                date=faker.date_this_year()
            ))
        Income.objects.bulk_create(incomes)

        # Gastos: parte ligados a compras reales (PurchaseBatch), parte operativos
        expenses = []
        # gastos ligados a lotes (si existen)
        for _ in range(min(8, max(1, len(batches)))):
            batch = random.choice(batches) if batches else None
            if batch:
                batch_total = getattr(batch, 'total_cost', None)
                if not batch_total or batch_total == 0:
                    # fallback estimado
                    batch_total = qd(Decimal(random.uniform(50, 300)))
                # sumar transporte y comisiones
                amount = qd(batch_total * Decimal(str(random.uniform(1.02, 1.12))))
                description = f"Pago a proveedor {faker.company()} por {batch.raw_material.name} (lote #{batch.id})"
                expenses.append(Expense(
                    tenant=tenant,
                    description=description,
                    amount=amount,
                    date=faker.date_this_year()
                ))

        # gastos operativos variados
        expense_templates = [
            "Pago de sueldos - nómina mensual",
            "Pago de transporte y logística",
            "Mantenimiento y afilado de herramientas",
            "Compra de suministros menores",
            "Gastos de electricidad y servicios"
        ]
        for _ in range(7):
            desc = random.choice(expense_templates) + " - " + faker.catch_phrase()
            amount = qd(Decimal(random.uniform(30, 900)))
            expenses.append(Expense(
                tenant=tenant,
                description=desc,
                amount=amount,
                date=faker.date_this_year()
            ))

        Expense.objects.bulk_create(expenses)

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        # Resumen
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  Tenant: {tenant.name}')
        self.stdout.write(f'  Admin user: {admin_user.email}')
        self.stdout.write(f'  Raw materials: {RawMaterial.objects.count()}')
        self.stdout.write(f'  Products: {Product.objects.count()}')
        self.stdout.write(f'  Purchase batches: {PurchaseBatch.objects.count()}')
        self.stdout.write(f'  Production logs: {ProductionLog.objects.count()}')
        self.stdout.write(f'  Incomes: {Income.objects.count()}')
        self.stdout.write(f'  Expenses: {Expense.objects.count()}')
