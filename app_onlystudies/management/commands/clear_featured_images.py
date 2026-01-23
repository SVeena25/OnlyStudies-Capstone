from django.core.management.base import BaseCommand
from app_onlystudies.models import BlogPost


class Command(BaseCommand):
    help = 'Clear all featured images from blog posts to fix 404 errors on Heroku'

    def handle(self, *args, **options):
        """
        Clear the featured_image field from all BlogPost instances.
        This is useful when migrating to Cloudinary or when local media files
        are not available on the deployment server.
        """
        blog_posts = BlogPost.objects.exclude(featured_image='')
        count = blog_posts.count()
        
        if count == 0:
            self.stdout.write(
                self.style.WARNING('No blog posts with featured images found.')
            )
            return
        
        # Clear all featured images
        for post in blog_posts:
            post.featured_image = ''
            post.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleared featured images from {count} blog post(s).'
            )
        )
