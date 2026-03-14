from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils.text import slugify
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary import uploader
from cloudinary.utils import cloudinary_url
from .forms import (
    SignUpForm,
    ForumQuestionForm,
    ForumAnswerForm,
    AppointmentForm,
    BlogPostForm,
    BlogCommentForm,
    TaskForm,
)
from .models import (
    Category,
    SubCategory,
    BlogPost,
    BlogComment,
    BlogPostVote,
    Notification,
    ForumQuestion,
    ForumAnswer,
    Task,
    Appointment,
)


def _safe_blog_image_url(image_field):
    """Return a safe image URL for blog images, with production fallbacks."""
    fallback = '/static/img/blog.png'
    if not image_field:
        return None

    image_name = (getattr(image_field, 'name', '') or '').strip()

    # Legacy rows may store a direct URL string instead of a storage key.
    if image_name.startswith('http://') or image_name.startswith('https://'):
        return image_name

    is_production = getattr(settings, 'IS_PRODUCTION', False)
    has_cloudinary_storage = getattr(settings, 'HAS_CLOUDINARY_STORAGE', False)

    # Legacy values like blog/logo.png came from local media usage; prefer
    # static fallback.
    filename = image_name.rsplit(
        '/', 1)[-1] if '/' in image_name else image_name
    if image_name.startswith('blog/') and filename and '.' in filename:
        return f'/static/img/{filename}'

    # Build Cloudinary URL from public_id to avoid malformed /media/... URLs.
    if has_cloudinary_storage and image_name:
        try:
            image_url, _ = cloudinary_url(image_name, secure=is_production)
        except Exception:
            image_url = ''
    else:
        try:
            image_url = image_field.url
        except Exception:
            image_url = ''

    # Some invalid values are rendered as /media/https://... by storage
    # backends.
    # Prefer the original absolute URL when available.
    if image_url.startswith(
            '/media/http://') or image_url.startswith('/media/https://'):
        if (
            image_name.startswith('http://')
            or image_name.startswith('https://')
        ):
            return image_name
        return fallback

    if is_production:
        # Legacy DB rows can still store local media paths like
        # "blog/logo.png".
        # In production those files are unavailable, so prefer matching static
        # assets.
        if image_name.startswith('blog/'):
            filename = image_name.rsplit('/', 1)[-1]
            # Only treat legacy filename values (with extension) as local
            # static assets.
            if filename and '.' in filename:
                return f'/static/img/{filename}'

        # In production, avoid broken local-media paths and non-Cloudinary
        # remote URLs.
        if image_url.startswith('/media/'):
            filename = image_url.rsplit('/', 1)[-1]
            if filename:
                return f'/static/img/{filename}'
            return fallback
        if not has_cloudinary_storage:
            return fallback
        if 'res.cloudinary.com/' not in image_url:
            return fallback

    return image_url or fallback


class HomePage(TemplateView):
    """
    Displays home page
    """
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = BlogPost.objects.filter(
            is_published=True).select_related('author', 'category')[:6]
        for post in posts:
            post.display_image_url = _safe_blog_image_url(post.featured_image)
        context['home_blog_posts'] = posts
        return context


class AboutView(TemplateView):
    """
    Displays about page
    """
    template_name = 'core/about.html'


class TaskListView(LoginRequiredMixin, ListView):
    """
    List view for tasks with filtering and sorting by due date,
    priority, and category.
    """
    model = Task
    template_name = 'tasks/tasks.html'
    context_object_name = 'tasks'
    paginate_by = 20
    login_url = reverse_lazy('login')

    def get_queryset(self):
        qs = Task.objects.filter(
            created_by=self.request.user).select_related('category')

        # Filters
        category_slug = self.request.GET.get('category')
        priority = self.request.GET.get('priority')
        due_before = self.request.GET.get('due_before')
        due_after = self.request.GET.get('due_after')

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if priority in {'low', 'medium', 'high'}:
            qs = qs.filter(priority=priority)
        # Parse date filters (YYYY-MM-DD)
        from datetime import datetime
        date_fmt = '%Y-%m-%d'
        if due_before:
            try:
                dt = datetime.strptime(due_before, date_fmt)
                qs = qs.filter(due_date__date__lte=dt.date())
            except ValueError:
                pass
        if due_after:
            try:
                dt = datetime.strptime(due_after, date_fmt)
                qs = qs.filter(due_date__date__gte=dt.date())
            except ValueError:
                pass

        # Sorting
        sort = self.request.GET.get('sort')
        allowed_sorts = {
            'due_asc': 'due_date',
            'due_desc': '-due_date',
            'priority_asc': 'priority',
            'priority_desc': '-priority',
            'title_asc': 'title',
            'title_desc': '-title',
            'created_desc': '-created_at',
        }
        if sort in allowed_sorts:
            qs = qs.order_by(allowed_sorts[sort])

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['selected'] = {
            'category': self.request.GET.get('category') or '',
            'priority': self.request.GET.get('priority') or '',
            'due_before': self.request.GET.get('due_before') or '',
            'due_after': self.request.GET.get('due_after') or '',
            'sort': self.request.GET.get('sort') or '',
        }
        ctx['page_title'] = 'My Tasks'
        return ctx


class CreateTaskView(LoginRequiredMixin, CreateView):
    """
    View for creating a task
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/create_task.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tasks')


class DeleteTaskView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a task
    Only the creator can delete their own task
    """
    model = Task
    pk_url_kwarg = 'pk'
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks')
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != request.user:
            messages.error(
                request, 'You do not have permission to delete this task.')
            return redirect('tasks')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)


class SearchResultsView(TemplateView):
    """
    Simple search across blog posts and forum questions
    """
    template_name = 'core/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = (self.request.GET.get('q') or '').strip()

        blog_results = BlogPost.objects.none()
        forum_results = ForumQuestion.objects.none()

        if query:
            blog_results = BlogPost.objects.filter(
                is_published=True
            ).filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).select_related('author', 'category')

            forum_results = ForumQuestion.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).select_related('author', 'category')

        context['search_query'] = query
        context['blog_results'] = blog_results
        context['forum_results'] = forum_results
        return context


class SignUpView(CreateView):
    """
    User signup view with form validation and security
    """
    model = User
    form_class = SignUpForm
    template_name = 'core/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """
        Handle successful form submission
        """
        user = form.save()
        # Authenticate and login the user after signup
        raw_password = form.cleaned_data.get('password')
        authenticated_user = authenticate(
            self.request,
            username=user.username,
            password=raw_password
        )
        if authenticated_user is not None:
            login(self.request, authenticated_user)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Sign Up'
        return context


class CustomLoginView(LoginView):
    """
    Custom login view with security features
    """
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def get_default_redirect_url(self):
        """
        Role-based default redirect after successful login.
        Keeps LoginView's built-in `next` handling unchanged.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return reverse_lazy('admin:index')
        if user.groups.filter(name='Instructor').exists():
            return reverse_lazy('create_blog')
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Login'
        return context


class CustomLogoutView(LogoutView):
    """
    Custom logout view
    """
    next_page = reverse_lazy('home')


class CategoryView(TemplateView):
    """
    Display content filtered by category
    """
    template_name = 'categories/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug)
        subcategories = category.subcategories.all()

        context['category'] = category
        context['subcategories'] = subcategories
        context['page_title'] = f'{category.name} - OnlyStudies'

        return context


class SubCategoryView(TemplateView):
    """
    Display content filtered by subcategory
    """
    template_name = 'categories/subcategory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')

        category = get_object_or_404(Category, slug=category_slug)
        subcategory = get_object_or_404(
            SubCategory, category=category, slug=subcategory_slug)

        context['category'] = category
        context['subcategory'] = subcategory
        context['page_title'] = f'{subcategory.name} - OnlyStudies'

        return context


# API Views for Blog and Notifications
def blog_feed_api(request):
    """
    API endpoint to fetch blog posts
    Returns latest 5 published blog posts as JSON
    """
    blog_posts = BlogPost.objects.filter(is_published=True)[:5]
    blog_data = []

    for post in blog_posts:
        featured_image_url = _safe_blog_image_url(post.featured_image)

        blog_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:200],  # First 200 characters
            'author': post.author.get_full_name() or post.author.username,
            'category': post.category.name if post.category else 'General',
            'featured_image': featured_image_url,
            'created_at': post.created_at.isoformat(),
            'slug': post.slug,
        })

    return JsonResponse({'blogs': blog_data})


def notifications_api(request):
    """
    API endpoint to fetch user notifications
    Returns latest 5 unread notifications for logged-in user
    """
    if not request.user.is_authenticated:
        # Require authentication for notifications API
        return JsonResponse({'detail': 'Authentication required'}, status=401)

    try:
        notifications = Notification.objects.filter(
            user=request.user, is_read=False).order_by('-created_at')[:5]
        notifications_data = []

        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'url': notification.related_url,
            })

        return JsonResponse({'notifications': notifications_data})
    except Exception as e:
        return JsonResponse({'notifications': [], 'error': str(e)})


class NotificationsView(LoginRequiredMixin, ListView):
    """Full notifications list for the current user"""
    model = Notification
    template_name = 'notifications/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user).order_by('-created_at')


class BlogPostDetailView(DetailView):
    """
    View for displaying a single blog post
    """
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Return only published blog posts"""
        return BlogPost.objects.filter(
            is_published=True).select_related(
            'author', 'category')

    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = context['post'].title
        context['is_production'] = getattr(settings, 'IS_PRODUCTION', False)
        context['has_cloudinary_storage'] = getattr(
            settings, 'HAS_CLOUDINARY_STORAGE', False)
        context['post_image_url'] = _safe_blog_image_url(
            context['post'].featured_image)

        # Get related posts from the same category (exclude current post)
        post = context['post']
        related_posts = BlogPost.objects.filter(
            is_published=True,
            category=post.category
        ).exclude(id=post.id).select_related('author', 'category')[:4]

        for related_post in related_posts:
            related_post.display_image_url = _safe_blog_image_url(
                related_post.featured_image)

        context['related_posts'] = related_posts
        context['comments'] = post.comments.filter(
            is_approved=True).select_related('author')
        context['comment_form'] = BlogCommentForm()
        context['upvote_count'] = post.upvote_count
        context['downvote_count'] = post.downvote_count
        context['vote_score'] = post.vote_score
        context['current_user_vote'] = 0
        if self.request.user.is_authenticated:
            existing_vote = BlogPostVote.objects.filter(
                blog_post=post, user=self.request.user).first()
            if existing_vote:
                context['current_user_vote'] = existing_vote.value

        return context


class CreateBlogPostView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Public create flow for news/blog stories with publishing permissions.
    """
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/create_blog_post.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        user = self.request.user
        return (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name='Instructor').exists()
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(
                f"{reverse_lazy('login')}?next={self.request.path}")
        messages.error(
            self.request, 'You do not have permission to create news stories.')
        return redirect('home')

    def form_valid(self, form):
        form.instance.author = self.request.user

        base_slug = slugify(form.cleaned_data.get(
            'title', 'news-story')) or 'news-story'
        slug = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        form.instance.slug = slug

        cloudinary_image_link = (form.cleaned_data.get(
            'cloudinary_image_link') or '').strip()
        if cloudinary_image_link:
            try:
                upload_result = uploader.upload(
                    cloudinary_image_link, folder='blog')
                public_id = upload_result.get('public_id')
                if public_id:
                    form.instance.featured_image = public_id
            except Exception as exc:
                messages.warning(
                    self.request,
                    f'Post will be saved, but image import failed: {exc}')

        # Only staff/superusers can publish immediately.
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            form.instance.is_published = False
            messages.info(
                self.request,
                (
                    'Story submitted successfully. It is pending review '
                    'before publication.'
                ),
            )
        else:
            messages.success(
                self.request,
                'Your news story has been published successfully!')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create News Story'
        context['can_publish'] = (
            self.request.user.is_staff
            or self.request.user.is_superuser
        )
        return context

    def get_success_url(self):
        if self.object.is_published:
            return reverse_lazy(
                'blog_detail', kwargs={
                    'slug': self.object.slug})
        return reverse_lazy('home')


@require_http_methods(['POST'])
def post_blog_comment(request, slug):
    """
    Post a comment on a published blog/news story.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to post a comment.')
        return redirect(f"{reverse_lazy('login')}?next={request.path}")

    post = get_object_or_404(
        BlogPost.objects.filter(is_published=True), slug=slug)
    form = BlogCommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.blog_post = post
        comment.author = request.user
        comment.save()
        messages.success(request, 'Your comment has been posted.')
    else:
        messages.error(
            request, 'Please enter a valid comment (at least 3 characters).')

    return redirect('blog_detail', slug=slug)


@require_http_methods(['POST'])
def vote_blog_post(request, slug, vote_type):
    """
    Upvote/downvote a published blog post. Repeating the same vote removes it.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to vote.')
        return redirect(f"{reverse_lazy('login')}?next={request.path}")

    post = get_object_or_404(
        BlogPost.objects.filter(is_published=True), slug=slug)
    vote_value = (
        BlogPostVote.UPVOTE if vote_type == 'up' else BlogPostVote.DOWNVOTE
    )

    if vote_type not in {'up', 'down'}:
        messages.error(request, 'Invalid vote action.')
        return redirect('blog_detail', slug=slug)

    existing_vote = BlogPostVote.objects.filter(
        blog_post=post, user=request.user).first()

    if existing_vote and existing_vote.value == vote_value:
        existing_vote.delete()
        messages.info(request, 'Your vote was removed.')
    elif existing_vote:
        existing_vote.value = vote_value
        existing_vote.save(update_fields=['value', 'updated_at'])
        messages.success(request, 'Your vote was updated.')
    else:
        BlogPostVote.objects.create(
            blog_post=post, user=request.user, value=vote_value)
        messages.success(request, 'Your vote was recorded.')

    return redirect('blog_detail', slug=slug)


class ForumView(ListView):
    """
    View for displaying forum questions
    """
    model = ForumQuestion
    template_name = 'forum/forum.html'
    context_object_name = 'questions'
    paginate_by = 15

    def get_queryset(self):
        """Return forum questions with related data"""
        return ForumQuestion.objects.select_related(
            'author', 'category').prefetch_related('answers')

    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Student Forum'
        context['categories'] = Category.objects.all()
        return context


class ForumQuestionDetailView(DetailView):
    """
    View for displaying a single forum question with answers
    """
    model = ForumQuestion
    template_name = 'forum/forum_question.html'
    context_object_name = 'question'

    def get_object(self):
        """Get question and increment view count"""
        question = get_object_or_404(ForumQuestion, slug=self.kwargs['slug'])
        question.views += 1
        question.save(update_fields=['views'])
        return question

    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.title
        context['answer_form'] = ForumAnswerForm()
        context['answers'] = self.object.answers.select_related('author')
        return context


class AskQuestionView(LoginRequiredMixin, CreateView):
    """
    View for creating forum questions
    """
    model = ForumQuestion
    form_class = ForumQuestionForm
    template_name = 'forum/ask_question.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        """Set the author to the current user"""
        form.instance.author = self.request.user
        messages.success(
            self.request, 'Your question has been posted successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the question detail page"""
        return reverse_lazy(
            'forum_question', kwargs={
                'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Ask a Question'
        return context


class AppointmentListView(LoginRequiredMixin, ListView):
    """
    List all appointments for the current user.
    """
    model = Appointment
    template_name = 'appointments/appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return Appointment.objects.filter(
            created_by=self.request.user).order_by('appointment_datetime')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'My Appointments'
        return ctx


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """
    Simple booking view for creating an appointment.
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/book_appointment.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request, 'Your appointment has been booked successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('appointments')


def post_answer(request, slug):
    """
    View for posting answers to forum questions
    """
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to post an answer.')
        return redirect('login')

    question = get_object_or_404(ForumQuestion, slug=slug)

    if request.method == 'POST':
        form = ForumAnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()

            # Mark question as answered if it's the first answer
            if not question.is_answered:
                question.is_answered = True
                question.save(update_fields=['is_answered'])

            messages.success(request, 'Your answer has been posted!')
            return redirect('forum_question', slug=slug)
        else:
            messages.error(request, 'Please correct the errors below.')

    return redirect('forum_question', slug=slug)


def apply_exam(request, exam_name):
    """
    Simple view for exam application (test purpose only)
    """
    context = {
        'exam_name': exam_name.replace('-', ' ').title(),
        'page_title': f'Apply for {exam_name.replace("-", " ").title()}'
    }
    return render(request, 'core/apply_exam.html', context)


class IsAuthorMixin(UserPassesTestMixin):
    """
    Mixin to check if the user can manage the object
    Allows object authors and admin users (staff/superuser).
    """

    def test_func(self):
        obj = self.get_object()
        return (
            obj.author == self.request.user
            or self.request.user.is_staff
            or self.request.user.is_superuser
        )

    def handle_no_permission(self):
        messages.error(
            self.request, 'You do not have permission to delete this item.')
        return redirect(self.request.META.get('HTTP_REFERER', 'forum'))


class UpdateBlogPostView(LoginRequiredMixin, IsAuthorMixin, UpdateView):
    """
    View for updating a blog post
    Only the author can update their own post
    """
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/edit_blog_post.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def test_func(self):
        user = self.request.user
        role_allowed = (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name='Instructor').exists()
        )
        return role_allowed and super().test_func()

    def handle_no_permission(self):
        messages.error(
            self.request, 'You do not have permission to manage blog posts.')
        return redirect('home')

    def form_valid(self, form):
        """Update post and optionally import image from Cloudinary link."""
        cloudinary_image_link = (form.cleaned_data.get(
            'cloudinary_image_link') or '').strip()

        if cloudinary_image_link:
            try:
                upload_result = uploader.upload(
                    cloudinary_image_link, folder='blog')
                public_id = upload_result.get('public_id')
                if public_id:
                    form.instance.featured_image = public_id
            except Exception as exc:
                # Keep existing image if link import fails, but still save text
                # fields.
                self.object = self.get_object()
                self.object.title = form.cleaned_data['title']
                self.object.content = form.cleaned_data['content']
                self.object.category = form.cleaned_data.get('category')
                self.object.is_published = form.cleaned_data.get(
                    'is_published', False)
                self.object.save(
                    update_fields=[
                        'title',
                        'content',
                        'category',
                        'is_published',
                        'updated_at'])
                messages.warning(
                    self.request,
                    f'Post updated, but Cloudinary image import failed: {exc}'
                )
                return redirect(self.get_success_url())

        try:
            response = super().form_valid(form)
            messages.success(
                self.request, 'Your blog post has been updated successfully!')
            return response
        except CloudinaryError:
            self.object = self.get_object()
            self.object.title = form.cleaned_data['title']
            self.object.content = form.cleaned_data['content']
            self.object.category = form.cleaned_data.get('category')
            self.object.is_published = form.cleaned_data.get(
                'is_published', False)
            self.object.save(
                update_fields=[
                    'title',
                    'content',
                    'category',
                    'is_published',
                    'updated_at'])
            messages.warning(
                self.request,
                (
                    'Your post was updated, but the new image could not be '
                    'uploaded. The previous image was kept.'
                )
            )
            return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """Provide a safe preview URL for the current featured image."""
        context = super().get_context_data(**kwargs)
        context['current_image_url'] = _safe_blog_image_url(
            self.object.featured_image)
        return context

    def get_success_url(self):
        """Redirect to the blog post detail page"""
        return reverse_lazy('blog_detail', kwargs={'slug': self.object.slug})


class UpdateForumQuestionView(LoginRequiredMixin, IsAuthorMixin, UpdateView):
    """
    View for updating a forum question
    Only the author can update their own question
    """
    model = ForumQuestion
    form_class = ForumQuestionForm
    template_name = 'forum/edit_forum_question.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        """Update the question and show success message"""
        messages.success(
            self.request, 'Your question has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the forum question detail page"""
        return reverse_lazy(
            'forum_question', kwargs={
                'slug': self.object.slug})


class UpdateForumAnswerView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        UpdateView):
    """
    View for updating a forum answer
    Only the author can update their own answer
    """
    model = ForumAnswer
    form_class = ForumAnswerForm
    template_name = 'forum/edit_forum_answer.html'
    pk_url_kwarg = 'answer_id'
    login_url = reverse_lazy('login')

    def test_func(self):
        """Check if user is the author of the answer"""
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        """Handle permission denied"""
        messages.error(
            self.request, 'You do not have permission to edit this answer.')
        return redirect(self.request.META.get('HTTP_REFERER', 'forum'))

    def form_valid(self, form):
        """Update the answer and show success message"""
        messages.success(
            self.request, 'Your answer has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to the question"""
        return reverse_lazy(
            'forum_question', kwargs={
                'slug': self.object.question.slug})


class UpdateTaskView(LoginRequiredMixin, UpdateView):
    """
    View for updating a task
    Only the creator can update their own task
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/edit_task.html'
    pk_url_kwarg = 'pk'
    login_url = reverse_lazy('login')

    def test_func(self):
        """Check if user created the task"""
        obj = self.get_object()
        return obj.created_by == self.request.user

    def dispatch(self, request, *args, **kwargs):
        """Check permissions before processing request"""
        obj = self.get_object()
        if obj.created_by != request.user:
            messages.error(
                request, 'You do not have permission to edit this task.')
            return redirect('tasks')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Update the task and show success message"""
        messages.success(
            self.request, 'Your task has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to tasks"""
        return reverse_lazy('tasks')


class UpdateAppointmentView(LoginRequiredMixin, UpdateView):
    """
    View for updating an appointment
    Only the creator can update their own appointment
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/edit_appointment.html'
    pk_url_kwarg = 'pk'
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        """Check permissions before processing request"""
        obj = self.get_object()
        if obj.created_by != request.user:
            messages.error(
                request,
                'You do not have permission to edit this appointment.')
            return redirect('appointments')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Update the appointment and show success message"""
        messages.success(
            self.request, 'Your appointment has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect back to appointments"""
        return reverse_lazy('appointments')


class DeleteAppointmentView(LoginRequiredMixin, DeleteView):
    """
    View for deleting an appointment.
    Only the creator can delete their own appointment.
    """
    model = Appointment
    pk_url_kwarg = 'pk'
    template_name = 'appointments/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointments')
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != request.user:
            messages.error(
                request,
                'You do not have permission to delete this appointment.')
            return redirect('appointments')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(
            request, 'Your appointment has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DeleteForumQuestionView(LoginRequiredMixin, IsAuthorMixin, DeleteView):
    """
    View for deleting a forum question
    Only the author can delete their own question
    """
    model = ForumQuestion
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'forum/forumquestion_confirm_delete.html'
    success_url = reverse_lazy('forum')
    login_url = reverse_lazy('login')

    def delete(self, request, *args, **kwargs):
        """Delete the question and show success message"""
        messages.success(
            request, 'Your question has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DeleteForumAnswerView(LoginRequiredMixin, IsAuthorMixin, DeleteView):
    """
    View for deleting a forum answer
    Only the author can delete their own answer
    """
    model = ForumAnswer
    pk_url_kwarg = 'answer_id'
    template_name = 'forum/forumanswer_confirm_delete.html'
    login_url = reverse_lazy('login')

    def get_success_url(self):
        """Redirect back to the question"""
        return reverse_lazy(
            'forum_question', kwargs={
                'slug': self.object.question.slug})

    def delete(self, request, *args, **kwargs):
        """Delete the answer and show success message"""
        messages.success(request, 'Your answer has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DeleteBlogPostView(LoginRequiredMixin, IsAuthorMixin, DeleteView):
    """
    View for deleting a blog post
    Only the author can delete their own post
    """
    model = BlogPost
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('login')

    def test_func(self):
        user = self.request.user
        role_allowed = (
            user.is_staff
            or user.is_superuser
            or user.groups.filter(name='Instructor').exists()
        )
        return role_allowed and super().test_func()

    def handle_no_permission(self):
        messages.error(
            self.request, 'You do not have permission to manage blog posts.')
        return redirect('home')

    def delete(self, request, *args, **kwargs):
        """Delete the blog post and show success message"""
        messages.success(
            request, 'Your blog post has been deleted successfully!')
        return super().delete(request, *args, **kwargs)
