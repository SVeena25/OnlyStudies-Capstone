from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app_onlystudies.models import BlogPost, Notification, Category


class Command(BaseCommand):
    help = 'Populate blog posts and notifications with sample data'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@onlystudies.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )

        # Get first category
        category = Category.objects.first()
        if not category:
            category = Category.objects.create(
                name='General',
                slug='general',
                description='General posts'
            )

        # Create sample blog posts
        blog_posts = [
            {
                'title': 'Tips for Passing Your MBA Exams',
                'content': (
                    'Use a weekly plan, practice papers, and revision blocks '
                    'to improve consistency and confidence before exam day.'
                ),
                'author': admin_user,
                'category': category,
                'slug': 'tips-for-passing-mba-exams',
                'is_published': True,
            },
            {
                'title': 'Engineering Mathematics Essentials',
                'content': (
                    'Focus on calculus, linear algebra, and differential '
                    'equations with worked examples and timed practice sets.'
                ),
                'author': admin_user,
                'category': category,
                'slug': 'engineering-mathematics-essentials',
                'is_published': True,
            },
            {
                'title': 'Medical Terminology for Healthcare Professionals',
                'content': (
                    'Learn common roots, prefixes, and suffixes to read '
                    'clinical terms faster and communicate with clarity.'
                ),
                'author': admin_user,
                'category': category,
                'slug': 'medical-terminology-healthcare',
                'is_published': True,
            },
            {
                'title': 'Effective Study Techniques for Online Learning',
                'content': (
                    'Build a distraction-free routine, take active notes, and '
                    'review progress weekly to maintain momentum online.'
                ),
                'author': admin_user,
                'category': category,
                'slug': 'effective-study-techniques',
                'is_published': True,
            },
            {
                'title': 'Time Management for Competitive Exams',
                'content': (
                    'Break the syllabus into small goals, track mock scores, '
                    'and reserve time each week for targeted revision.'
                ),
                'author': admin_user,
                'category': category,
                'slug': 'time-management-competitive-exams',
                'is_published': True,
            },
        ]

        for blog_data in blog_posts:
            blog, created = BlogPost.objects.get_or_create(
                slug=blog_data['slug'],
                defaults=blog_data
            )
            if created:
                self.stdout.write(f'Created blog post: {blog.title}')
            else:
                self.stdout.write(f'Blog post already exists: {blog.title}')

        # Create sample notifications
        notifications = [
            {
                'user': admin_user,
                'title': 'Welcome to OnlyStudies',
                'message': (
                    'Welcome to OnlyStudies. Explore resources and plan your '
                    'next study session today.'
                ),
                'notification_type': 'system',
                'is_read': False,
            },
            {
                'user': admin_user,
                'title': 'New Blog Post Published',
                'message': (
                    'A new study article is available in the blog feed. '
                    'Read it when you have a free moment.'
                ),
                'notification_type': 'course',
                'is_read': False,
            },
            {
                'user': admin_user,
                'title': 'Achievement Unlocked',
                'message': (
                    'Great progress this week. Keep the streak going with one '
                    'more focused session.'
                ),
                'notification_type': 'achievement',
                'is_read': False,
            },
        ]

        for notif_data in notifications:
            notif, created = Notification.objects.get_or_create(
                user=notif_data['user'],
                title=notif_data['title'],
                defaults=notif_data
            )
            if created:
                self.stdout.write(f'Created notification: {notif.title}')
            else:
                self.stdout.write(
                    f'Notification already exists: {notif.title}')

        self.stdout.write(self.style.SUCCESS(
            'Successfully populated blog posts and notifications'))
