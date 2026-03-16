from django.db import migrations


def seed_default_categories(apps, schema_editor):
    Category = apps.get_model('app_onlystudies', 'Category')
    SubCategory = apps.get_model('app_onlystudies', 'SubCategory')

    categories = (
        (
            'mba',
            'MBA',
            'Master of Business Administration courses and resources',
            (
                (
                    'finance',
                    'Finance',
                    'Financial management, accounting, and investment courses',
                ),
                (
                    'marketing',
                    'Marketing',
                    'Digital marketing, brand management, and market strategy',
                ),
                (
                    'operations',
                    'Operations',
                    'Supply chain, operations management, and logistics',
                ),
            ),
        ),
        (
            'engineering',
            'Engineering',
            'Engineering courses covering various disciplines',
            (
                (
                    'computer-science',
                    'Computer Science',
                    'Programming, algorithms, and software development',
                ),
                (
                    'mechanical',
                    'Mechanical',
                    'Mechanical design, thermodynamics, and manufacturing',
                ),
                (
                    'civil',
                    'Civil',
                    'Structural design, construction, and infrastructure',
                ),
            ),
        ),
        (
            'medical',
            'Medical',
            'Medical education and healthcare studies',
            (
                (
                    'mbbs',
                    'MBBS',
                    'Bachelor of Medicine, Bachelor of Surgery',
                ),
                (
                    'neet',
                    'NEET',
                    'National Eligibility cum Entrance Test preparation',
                ),
                (
                    'nursing',
                    'Nursing',
                    'Nursing education and healthcare certification',
                ),
            ),
        ),
    )

    for category_slug, category_name, category_description, subcategories in categories:
        category, _ = Category.objects.get_or_create(
            slug=category_slug,
            defaults={
                'name': category_name,
                'description': category_description,
            },
        )

        for subcategory_slug, subcategory_name, subcategory_description in subcategories:
            SubCategory.objects.get_or_create(
                category=category,
                slug=subcategory_slug,
                defaults={
                    'name': subcategory_name,
                    'description': subcategory_description,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('app_onlystudies', '0008_appointment_appointment_datetime_not_before_created_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_default_categories, migrations.RunPython.noop),
    ]