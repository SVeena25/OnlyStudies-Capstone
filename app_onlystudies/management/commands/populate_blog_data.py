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
                'content': 'Passing your MBA exams requires dedication, smart study techniques, and proper time management. In this comprehensive guide, we explore the most effective strategies used by top performers. Start by understanding the exam pattern and syllabus thoroughly. Create a study schedule that covers all topics systematically. Use practice tests regularly to identify weak areas and work on them. Join study groups with peers to share knowledge and clarify doubts. Don\'t neglect sleep and exercise during your study period.',
                'author': admin_user,
                'category': category,
                'slug': 'tips-for-passing-mba-exams',
                'is_published': True,
            },
            {
                'title': 'Engineering Mathematics Essentials',
                'content': 'Mathematics is the foundation of engineering. Whether you\'re studying mechanical, electrical, civil, or chemical engineering, strong mathematical concepts are crucial. This article covers essential topics including calculus, differential equations, linear algebra, and complex numbers. We break down difficult concepts into easy-to-understand explanations with practical examples. Learn how to apply mathematical principles to real-world engineering problems and strengthen your problem-solving abilities.',
                'author': admin_user,
                'category': category,
                'slug': 'engineering-mathematics-essentials',
                'is_published': True,
            },
            {
                'title': 'Medical Terminology for Healthcare Professionals',
                'content': 'Understanding medical terminology is essential for anyone pursuing a career in healthcare. This comprehensive guide covers the fundamentals of medical terminology, including prefixes, suffixes, and root words. Learn about body systems, diseases, and treatments using proper medical language. Master pronunciation and spelling of complex medical terms. Whether you\'re a nursing student, medical student, or healthcare professional, this guide will help you communicate effectively in clinical settings.',
                'author': admin_user,
                'category': category,
                'slug': 'medical-terminology-healthcare',
                'is_published': True,
            },
            {
                'title': 'Effective Study Techniques for Online Learning',
                'content': 'Online learning has become increasingly popular, offering flexibility and accessibility. However, it requires different study strategies compared to traditional classroom learning. Create a dedicated study space free from distractions. Set specific goals for each study session. Use active learning techniques like note-taking, summarization, and self-quizzing. Schedule regular breaks to maintain focus and prevent burnout. Engage with online communities to stay motivated. Track your progress and adjust your strategies as needed.',
                'author': admin_user,
                'category': category,
                'slug': 'effective-study-techniques',
                'is_published': True,
            },
            {
                'title': 'Time Management for Competitive Exams',
                'content': 'Time management is critical when preparing for competitive exams. With limited time and vast syllabus, strategic planning becomes essential. Start your preparation early to avoid last-minute rush. Create a realistic study plan that covers all topics with adequate revision time. Use the Pomodoro technique or similar methods to maintain focus during study sessions. Practice time management during mock tests to improve speed and accuracy. Remember, consistent effort over a longer period beats cramming at the last minute.',
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
                'message': 'Welcome to OnlyStudies! Start exploring our comprehensive study materials and prepare for your exams with confidence.',
                'notification_type': 'system',
                'is_read': False,
            },
            {
                'user': admin_user,
                'title': 'New Blog Post Published',
                'message': 'Check out our latest blog post on effective study techniques for online learning.',
                'notification_type': 'course',
                'is_read': False,
            },
            {
                'user': admin_user,
                'title': 'Achievement Unlocked',
                'message': 'Congratulations! You\'ve completed 5 study sessions this week.',
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
                self.stdout.write(f'Notification already exists: {notif.title}')

        self.stdout.write(self.style.SUCCESS('Successfully populated blog posts and notifications'))
