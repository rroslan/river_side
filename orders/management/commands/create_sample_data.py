from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vendors.models import Vendor, Category, MenuItem, Table
from orders.models import Order, OrderItem
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Create sample data for River Side Food Court'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            MenuItem.objects.all().delete()
            Category.objects.all().delete()
            Vendor.objects.all().delete()
            Table.objects.all().delete()

        self.create_tables()
        self.create_vendors_and_menu()
        self.create_sample_orders()

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data for River Side Food Court!')
        )

    def create_tables(self):
        self.stdout.write('Creating tables...')

        # Create 25 tables
        for i in range(1, 26):
            Table.objects.get_or_create(
                number=i,
                defaults={
                    'seats': random.choice([2, 4, 6, 8]),
                    'is_active': True
                }
            )

        self.stdout.write(f'Created {Table.objects.count()} tables')

    def create_vendors_and_menu(self):
        self.stdout.write('Creating vendors and menu items...')

        # Create admin user for vendors
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@riverside.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # Create vendor users
        drink_vendor_user, _ = User.objects.get_or_create(
            username='drink_vendor',
            defaults={
                'email': 'drinks@riverside.com',
                'first_name': 'Fresh',
                'last_name': 'Beverages'
            }
        )

        asian_vendor_user, _ = User.objects.get_or_create(
            username='asian_vendor',
            defaults={
                'email': 'asian@riverside.com',
                'first_name': 'Asian',
                'last_name': 'Delights'
            }
        )

        pizza_vendor_user, _ = User.objects.get_or_create(
            username='pizza_vendor',
            defaults={
                'email': 'pizza@riverside.com',
                'first_name': 'Pizza',
                'last_name': 'Corner'
            }
        )

        # Create Drinks Vendor
        drinks_vendor, _ = Vendor.objects.get_or_create(
            name="Fresh Juice & Coffee Bar",
            defaults={
                'vendor_type': 'drinks',
                'description': 'Fresh squeezed juices, smoothies, coffee and tea',
                'owner': drink_vendor_user,
                'is_active': True
            }
        )

        # Drinks Categories and Items
        juice_category, _ = Category.objects.get_or_create(
            name="Fresh Juices",
            vendor=drinks_vendor,
            defaults={'description': 'Freshly squeezed juices', 'sort_order': 1}
        )

        coffee_category, _ = Category.objects.get_or_create(
            name="Coffee & Tea",
            vendor=drinks_vendor,
            defaults={'description': 'Hot and cold coffee and tea', 'sort_order': 2}
        )

        smoothie_category, _ = Category.objects.get_or_create(
            name="Smoothies",
            vendor=drinks_vendor,
            defaults={'description': 'Healthy fruit and veggie smoothies', 'sort_order': 3}
        )

        # Juice items
        juice_items = [
            ('Orange Juice', 'Freshly squeezed orange juice', 4.50, True, True, 110),
            ('Apple Juice', 'Fresh apple juice with no added sugar', 4.00, True, True, 95),
            ('Carrot Ginger Juice', 'Fresh carrot juice with ginger kick', 5.50, True, True, 80),
            ('Green Juice', 'Spinach, cucumber, apple, and lemon', 6.50, True, True, 65),
            ('Watermelon Juice', 'Fresh watermelon juice', 4.50, True, True, 85),
        ]

        for name, desc, price, veg, vegan, calories in juice_items:
            MenuItem.objects.get_or_create(
                name=name,
                category=juice_category,
                defaults={
                    'description': desc,
                    'price': Decimal(str(price)),
                    'is_available': True,
                    'is_vegetarian': veg,
                    'is_vegan': vegan,
                    'calories': calories,
                    'preparation_time': 3
                }
            )

        # Coffee items
        coffee_items = [
            ('Cappuccino', 'Rich espresso with steamed milk foam', 3.50, True, False, 120),
            ('Latte', 'Smooth espresso with steamed milk', 4.00, True, False, 150),
            ('Americano', 'Espresso with hot water', 3.00, True, True, 15),
            ('Cold Brew', 'Smooth cold coffee concentrate', 3.50, True, True, 25),
            ('Green Tea', 'Premium loose leaf green tea', 2.50, True, True, 0),
            ('Chai Latte', 'Spiced tea with steamed milk', 4.50, True, False, 180),
        ]

        for name, desc, price, veg, vegan, calories in coffee_items:
            MenuItem.objects.get_or_create(
                name=name,
                category=coffee_category,
                defaults={
                    'description': desc,
                    'price': Decimal(str(price)),
                    'is_available': True,
                    'is_vegetarian': veg,
                    'is_vegan': vegan,
                    'calories': calories,
                    'preparation_time': 5
                }
            )

        # Smoothie items
        smoothie_items = [
            ('Mango Smoothie', 'Fresh mango with coconut milk', 6.50, True, True, 220),
            ('Berry Blast', 'Mixed berries with banana and yogurt', 7.00, True, False, 180),
            ('Green Power', 'Spinach, apple, banana, and protein powder', 8.50, True, True, 250),
            ('Tropical Paradise', 'Pineapple, mango, and coconut water', 7.50, True, True, 200),
        ]

        for name, desc, price, veg, vegan, calories in smoothie_items:
            MenuItem.objects.get_or_create(
                name=name,
                category=smoothie_category,
                defaults={
                    'description': desc,
                    'price': Decimal(str(price)),
                    'is_available': True,
                    'is_vegetarian': veg,
                    'is_vegan': vegan,
                    'calories': calories,
                    'preparation_time': 4
                }
            )

        # Create Asian Food Vendor
        asian_vendor, _ = Vendor.objects.get_or_create(
            name="Asian Delights",
            defaults={
                'vendor_type': 'food',
                'description': 'Authentic Asian cuisine from Thailand, China, and Japan',
                'owner': asian_vendor_user,
                'is_active': True
            }
        )

        # Asian Categories
        noodles_category, _ = Category.objects.get_or_create(
            name="Noodles",
            vendor=asian_vendor,
            defaults={'description': 'Stir-fried and soup noodles', 'sort_order': 1}
        )

        rice_category, _ = Category.objects.get_or_create(
            name="Rice Dishes",
            vendor=asian_vendor,
            defaults={'description': 'Fried rice and rice bowls', 'sort_order': 2}
        )

        appetizers_category, _ = Category.objects.get_or_create(
            name="Appetizers",
            vendor=asian_vendor,
            defaults={'description': 'Small plates and starters', 'sort_order': 3}
        )

        # Noodle items
        noodle_items = [
            ('Pad Thai', 'Thai stir-fried rice noodles with shrimp', 12.90, False, False, 15, True, 'Rice noodles, shrimp, bean sprouts, eggs, tamarind sauce'),
            ('Chicken Lo Mein', 'Soft noodles with chicken and vegetables', 11.50, False, False, 12, False, 'Lo mein noodles, chicken, mixed vegetables, soy sauce'),
            ('Vegetable Ramen', 'Japanese noodle soup with vegetables', 10.90, True, True, 18, False, 'Ramen noodles, vegetable broth, corn, seaweed, vegetables'),
            ('Beef Chow Fun', 'Wide rice noodles with beef and bean sprouts', 13.50, False, False, 14, False, 'Rice noodles, beef, bean sprouts, dark soy sauce'),
            ('Singapore Rice Noodles', 'Curry-flavored thin rice noodles', 12.50, False, False, 13, True, 'Rice vermicelli, curry powder, char siu, shrimp'),
        ]

        for name, desc, price, veg, vegan, prep_time, spicy, ingredients in noodle_items:
            MenuItem.objects.get_or_create(
                name=name,
                category=noodles_category,
                defaults={
                    'description': desc,
                    'price': Decimal(str(price)),
                    'is_available': True,
                    'is_vegetarian': veg,
                    'is_vegan': vegan,
                    'preparation_time': prep_time,
                    'is_spicy': spicy,
                    'ingredients': ingredients,
                    'calories': random.randint(350, 550)
                }
            )

        # Rice items
        rice_items = [
            ('Chicken Fried Rice', 'Wok-fried rice with chicken and vegetables', 11.90, False, False, 12, False, 'Jasmine rice, chicken, eggs, mixed vegetables'),
            ('Thai Basil Fried Rice', 'Spicy fried rice with Thai basil', 12.50, True, True, 10, True, 'Jasmine rice, Thai basil, chilies, garlic'),
            ('Korean Bibimbap', 'Mixed rice bowl with vegetables and egg', 13.90, True, False, 15, True, 'Rice, assorted vegetables, egg, gochujang sauce'),
            ('Teriyaki Chicken Bowl', 'Grilled chicken over rice', 12.90, False, False, 14, False, 'Rice, chicken, teriyaki sauce, steamed vegetables'),
        ]

        for name, desc, price, veg, vegan, prep_time, spicy, ingredients in rice_items:
            MenuItem.objects.get_or_create(
                name=name,
                category=rice_category,
                defaults={
                    'description': desc,
                    'price': Decimal(str(price)),
                    'is_available': True,
                    'is_vegetarian': veg,
                    'is_vegan': vegan,
                    'preparation_time': prep_time,
                    'is_spicy': spicy,
                    'ingredients': ingredients,
                    'calories': random.randint(400, 600)
                }
            )

        # Appetizer items
        appetizer_items = [
            ('Spring Rolls (4 pcs)', 'Crispy vegetable spring rolls', 6.50, True, True, 8, False, 'Spring roll wrapper, cabbage, carrots, glass noodles'),
            ('Chicken Satay (5 pcs)', 'Grilled chicken skewers with peanut sauce', 8.90, False, False, 12, False, 'Chicken, coconut milk, turmeric, peanut sauce'),
            ('Pork Dumplings (6 pcs)', 'Pan-fried pork dumplings', 7.90, False, False, 10, False, 'Dumpling wrapper, ground pork, ginger, garlic'),
            ('Edamame', 'Steamed soybeans with sea salt', 4.50, True, True, 5, False, 'Soybeans, sea salt'),
        ]

        for name, desc, price, veg, vegan, prep_time, spicy, ingredients in appetizer_items:
            MenuItem.objects.get_or_create(
                name=name,
                category=appetizers_category,
                defaults={
                    'description': desc,
                    'price': Decimal(str(price)),
                    'is_available': True,
                    'is_vegetarian': veg,
                    'is_vegan': vegan,
                    'preparation_time': prep_time,
                    'is_spicy': spicy,
                    'ingredients': ingredients,
                    'calories': random.randint(150, 350)
                }
            )

        # Create Pizza Vendor
        pizza_vendor, _ = Vendor.objects.get_or_create(
            name="Pizza Corner",
            defaults={
                'vendor_type': 'food',
                'description': 'Wood-fired pizzas and Italian favorites',
                'owner': pizza_vendor_user,
                'is_active': True
            }
        )

        # Pizza Categories
        pizza_category, _ = Category.objects.get_or_create(
            name="Pizzas",
            vendor=pizza_vendor,
            defaults={'description': 'Wood-fired artisan pizzas', 'sort_order': 1}
        )

        pasta_category, _ = Category.objects.get_or_create(
            name="Pasta",
            vendor=pizza_vendor,
            defaults={'description': 'Fresh pasta dishes', 'sort_order': 2}
        )

        # Pizza items
        pizza_items = [
            ('Margherita', 'Fresh mozzarella, tomato sauce, and basil', 14.90, True, False, 18, False, 'Pizza dough, tomato sauce, mozzarella, fresh basil'),
            ('Pepperoni', 'Classic pepperoni with mozzarella cheese', 16.90, False, False, 18, False, 'Pizza dough, tomato sauce, mozzarella, pepperoni'),
            ('Hawaiian', 'Ham and pineapple with mozzarella', 15.90, False, False, 18, False, 'Pizza dough, tomato sauce, mozzarella, ham, pineapple'),
            ('Meat Lovers', 'Pepperoni, sausage, bacon, and ham', 19.90, False, False, 20, False, 'Pizza dough, tomato sauce, mozzarella, assorted meats'),
            ('Veggie Supreme', 'Bell peppers, mushrooms, onions, olives', 17.90, True, False, 18, False, 'Pizza dough, tomato sauce, mozzarella, vegetables'),
            ('BBQ Chicken', 'BBQ sauce, chicken, red onions, cilantro', 18.90, False, False, 20, False, 'Pizza dough, BBQ sauce, mozzarella, chicken, onions'),
        ]

        for name, desc, price, veg, vegan, prep_time, spicy, ingredients in pizza_items:
            MenuItem.objects.get_or_create(
                name=name,
                category=pizza_category,
                defaults={
                    'description': desc,
                    'price': Decimal(str(price)),
                    'is_available': True,
                    'is_vegetarian': veg,
                    'is_vegan': vegan,
                    'preparation_time': prep_time,
                    'is_spicy': spicy,
                    'ingredients': ingredients,
                    'calories': random.randint(220, 320)
                }
            )

        # Pasta items
        pasta_items = [
            ('Spaghetti Carbonara', 'Creamy pasta with bacon and parmesan', 13.90, False, False, 15, False, 'Spaghetti, eggs, bacon, parmesan, black pepper'),
            ('Penne Arrabiata', 'Spicy tomato sauce with garlic and chilies', 11.90, True, True, 12, True, 'Penne pasta, tomatoes, garlic, chilies, herbs'),
            ('Fettuccine Alfredo', 'Rich cream sauce with parmesan cheese', 12.90, True, False, 14, False, 'Fettuccine, butter, cream, parmesan cheese'),
            ('Chicken Parmigiana', 'Breaded chicken with marinara and cheese', 16.90, False, False, 18, False, 'Chicken breast, breadcrumbs, marinara, mozzarella'),
        ]

        for name, desc, price, veg, vegan, prep_time, spicy, ingredients in pasta_items:
            MenuItem.objects.get_or_create(
                name=name,
                category=pasta_category,
                defaults={
                    'description': desc,
                    'price': Decimal(str(price)),
                    'is_available': True,
                    'is_vegetarian': veg,
                    'is_vegan': vegan,
                    'preparation_time': prep_time,
                    'is_spicy': spicy,
                    'ingredients': ingredients,
                    'calories': random.randint(450, 650)
                }
            )

        self.stdout.write(f'Created {Vendor.objects.count()} vendors with menu items')

    def create_sample_orders(self):
        self.stdout.write('Creating sample orders...')

        # Get some tables and menu items
        tables = list(Table.objects.all()[:5])
        menu_items = list(MenuItem.objects.all())

        statuses = ['pending', 'confirmed', 'preparing', 'ready']

        for i in range(10):
            table = random.choice(tables)
            order = Order.objects.create(
                table=table,
                customer_name=f'Customer {i+1}',
                customer_phone=f'555-{1000+i:04d}',
                status=random.choice(statuses),
                notes=f'Sample order {i+1}' if random.random() > 0.7 else ''
            )

            # Add 1-4 items to each order
            num_items = random.randint(1, 4)
            selected_items = random.sample(menu_items, min(num_items, len(menu_items)))

            for item in selected_items:
                quantity = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=quantity,
                    unit_price=item.price,
                    special_instructions='Extra sauce' if random.random() > 0.8 else ''
                )

            order.calculate_total()
            order.save()

        self.stdout.write(f'Created {Order.objects.count()} sample orders')
