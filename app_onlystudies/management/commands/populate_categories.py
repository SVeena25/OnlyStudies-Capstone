from django.core.management.base import BaseCommand
from app_onlystudies.models import Category, SubCategory
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Populate initial categories and subcategories'

    def handle(self, *args, **options):
        # Define categories and subcategories
        categories_data = {
            'MBA': {
                'description': 'Master of Business Administration courses and resources',
                'subcategories': [
                    {'name': 'Finance', 'description': 'Financial management, accounting, and investment courses'},
                    {'name': 'Marketing', 'description': 'Digital marketing, brand management, and market strategy'},
                    {'name': 'Operations', 'description': 'Supply chain, operations management, and logistics'},
                ]
            },
            'Engineering': {
                'description': 'Engineering courses covering various disciplines',
                'subcategories': [
                    {'name': 'Computer Science', 'description': 'Programming, algorithms, and software development'},
                    {'name': 'Mechanical', 'description': 'Mechanical design, thermodynamics, and manufacturing'},
                    {'name': 'Civil', 'description': 'Structural design, construction, and infrastructure'},
                ]
            },
            'Medical': {
                'description': 'Medical education and healthcare studies',
                'subcategories': [
                    {'name': 'MBBS', 'description': 'Bachelor of Medicine, Bachelor of Surgery'},
                    {'name': 'NEET', 'description': 'National Eligibility cum Entrance Test preparation'},
                    {'name': 'Nursing', 'description': 'Nursing education and healthcare certification'},
                ]
            },
        }

        # Create categories and subcategories
        for cat_name, cat_data in categories_data.items():
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'slug': slugify(cat_name),
                    'description': cat_data['description']
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {cat_name}'))
            else:
                self.stdout.write(f'Category already exists: {cat_name}')

            # Create subcategories
            for subcat_data in cat_data['subcategories']:
                subcategory, subcat_created = SubCategory.objects.get_or_create(
                    category=category,
                    name=subcat_data['name'],
                    defaults={
                        'slug': slugify(subcat_data['name']),
                        'description': subcat_data['description']
                    }
                )

                if subcat_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created subcategory: {subcat_data["name"]}')
                    )
                else:
                    self.stdout.write(f'  Subcategory already exists: {subcat_data["name"]}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated all categories and subcategories!')
        )
