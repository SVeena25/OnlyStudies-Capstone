from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """
    Category model for organizing content
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """
    Subcategory model for detailed categorization
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "SubCategories"
        unique_together = ('category', 'slug')
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class BlogPost(models.Model):
    """
    Blog Post model for blog feed
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_posts')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    slug = models.SlugField(unique=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def upvote_count(self):
        return self.votes.filter(value=1).count()

    @property
    def downvote_count(self):
        return self.votes.filter(value=-1).count()

    @property
    def vote_score(self):
        return self.upvote_count - self.downvote_count

    def __str__(self):
        return self.title


class BlogPostVote(models.Model):
    """
    Per-user vote for a blog post: +1 upvote or -1 downvote.
    """
    UPVOTE = 1
    DOWNVOTE = -1
    VALUE_CHOICES = (
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    )

    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_post_votes')
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('blog_post', 'user')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value__in=[1, -1]),
                name='blog_post_vote_value_valid',
            ),
        ]

    def __str__(self):
        vote_name = 'upvote' if self.value == self.UPVOTE else 'downvote'
        return f"{self.user.username} {vote_name} on {self.blog_post.title}"


class BlogComment(models.Model):
    """
    Comment model for user responses on blog/news stories.
    """
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.blog_post.title}"


class Notification(models.Model):
    """
    Notification model for user notifications
    """
    NOTIFICATION_TYPES = [
        ('course', 'Course Update'),
        ('forum', 'Forum Activity'),
        ('achievement', 'Achievement'),
        ('system', 'System Message'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    related_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ForumQuestion(models.Model):
    """
    Forum Question model for student forum
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_questions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_questions')
    slug = models.SlugField(unique=True, blank=True)
    is_answered = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while ForumQuestion.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def answer_count(self):
        return self.answers.count()


class ForumAnswer(models.Model):
    """
    Forum Answer model for replies to questions
    """
    question = models.ForeignKey(ForumQuestion, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_answers')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_accepted', 'created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['question'],
                condition=models.Q(is_accepted=True),
                name='single_accepted_answer_per_question',
            ),
        ]
    
    def __str__(self):
        return f"Answer by {self.author.username} on {self.question.title}"


class Task(models.Model):
    """
    Task model to support filtering and sorting by due date, priority, and category
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', 'priority', 'title']

    def __str__(self):
        return self.title


class Appointment(models.Model):
    """
    Simple appointment booking for services/events at a specific date and time.
    """
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    appointment_datetime = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_datetime', 'title']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(appointment_datetime__gte=models.F('created_at')),
                name='appointment_datetime_not_before_created',
            ),
        ]

    def clean(self):
        super().clean()
        if self.appointment_datetime and self.appointment_datetime <= timezone.now():
            raise ValidationError({'appointment_datetime': 'Appointment date/time must be in the future.'})

    def __str__(self):
        return f"{self.title} @ {self.appointment_datetime.isoformat()}"

