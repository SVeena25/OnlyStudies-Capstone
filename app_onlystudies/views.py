from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView, UpdateView
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
from .forms import SignUpForm, ForumQuestionForm, ForumAnswerForm, AppointmentForm, BlogPostForm, TaskForm
from .models import Category, SubCategory, BlogPost, Notification, ForumQuestion, ForumAnswer, Task, Appointment


class HomePage(TemplateView):
    """
    Displays home page
    """
    template_name = 'index.html'


class AboutView(TemplateView):
    """
    Displays about page
    """
    template_name = 'about.html'


class TaskListView(LoginRequiredMixin, ListView):
    """
    List view for tasks with filtering and sorting by due date, priority, and category.
    """
    model = Task
    template_name = 'tasks.html'
    context_object_name = 'tasks'
    paginate_by = 20
    login_url = reverse_lazy('login')

    def get_queryset(self):
        qs = Task.objects.filter(created_by=self.request.user).select_related('category')

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


class SearchResultsView(TemplateView):
    """
    Simple search across blog posts and forum questions
    """
    template_name = 'search_results.html'

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
    template_name = 'signup.html'
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
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

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
    template_name = 'category.html'
    
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
    template_name = 'subcategory.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        
        category = get_object_or_404(Category, slug=category_slug)
        subcategory = get_object_or_404(SubCategory, category=category, slug=subcategory_slug)
        
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
        featured_image_url = post.featured_image.url if post.featured_image else None
        if featured_image_url and getattr(settings, 'IS_PRODUCTION', False) and featured_image_url.startswith('/media/'):
            featured_image_url = '/static/img/blog.png'

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
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
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
    template_name = 'notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class BlogFeedView(ListView):
    """
    View for displaying blog feed
    Shows all published blog posts
    """
    model = BlogPost
    template_name = 'blog_feed.html'
    context_object_name = 'blog_posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Return only published blog posts"""
        return BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Blog Feed'
        context['is_production'] = getattr(settings, 'IS_PRODUCTION', False)
        return context


class BlogPostDetailView(DetailView):
    """
    View for displaying a single blog post
    """
    model = BlogPost
    template_name = 'blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Return only published blog posts"""
        return BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = context['post'].title
        context['is_production'] = getattr(settings, 'IS_PRODUCTION', False)
        
        # Get related posts from the same category (exclude current post)
        post = context['post']
        related_posts = BlogPost.objects.filter(
            is_published=True,
            category=post.category
        ).exclude(id=post.id).select_related('author', 'category')[:4]
        context['related_posts'] = related_posts
        
        return context


class ForumView(ListView):
    """
    View for displaying forum questions
    """
    model = ForumQuestion
    template_name = 'forum.html'
    context_object_name = 'questions'
    paginate_by = 15
    
    def get_queryset(self):
        """Return forum questions with related data"""
        return ForumQuestion.objects.select_related('author', 'category').prefetch_related('answers')
    
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
    template_name = 'forum_question.html'
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
    template_name = 'ask_question.html'
    login_url = reverse_lazy('login')
    
    def form_valid(self, form):
        """Set the author to the current user"""
        form.instance.author = self.request.user
        messages.success(self.request, 'Your question has been posted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to the question detail page"""
        return reverse_lazy('forum_question', kwargs={'slug': self.object.slug})
    
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
    template_name = 'appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return Appointment.objects.filter(created_by=self.request.user).order_by('appointment_datetime')

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
    template_name = 'book_appointment.html'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Your appointment has been booked successfully!')
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
    return render(request, 'apply_exam.html', context)


class IsAuthorMixin(UserPassesTestMixin):
    """
    Mixin to check if the user is the author of the object
    """
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to delete this item.')
        return redirect(self.request.META.get('HTTP_REFERER', 'forum'))


class UpdateBlogPostView(LoginRequiredMixin, IsAuthorMixin, UpdateView):
    """
    View for updating a blog post
    Only the author can update their own post
    """
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'edit_blog_post.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')
    
    def form_valid(self, form):
        """Update the blog post and show success message"""
        messages.success(self.request, 'Your blog post has been updated successfully!')
        return super().form_valid(form)
    
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
    template_name = 'edit_forum_question.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('login')
    
    def form_valid(self, form):
        """Update the question and show success message"""
        messages.success(self.request, 'Your question has been updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to the forum question detail page"""
        return reverse_lazy('forum_question', kwargs={'slug': self.object.slug})


class UpdateForumAnswerView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for updating a forum answer
    Only the author can update their own answer
    """
    model = ForumAnswer
    form_class = ForumAnswerForm
    template_name = 'edit_forum_answer.html'
    pk_url_kwarg = 'answer_id'
    login_url = reverse_lazy('login')
    
    def test_func(self):
        """Check if user is the author of the answer"""
        obj = self.get_object()
        return obj.author == self.request.user
    
    def handle_no_permission(self):
        """Handle permission denied"""
        messages.error(self.request, 'You do not have permission to edit this answer.')
        return redirect(self.request.META.get('HTTP_REFERER', 'forum'))
    
    def form_valid(self, form):
        """Update the answer and show success message"""
        messages.success(self.request, 'Your answer has been updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect back to the question"""
        return reverse_lazy('forum_question', kwargs={'slug': self.object.question.slug})


class UpdateTaskView(LoginRequiredMixin, UpdateView):
    """
    View for updating a task
    Only the creator can update their own task
    """
    model = Task
    form_class = TaskForm
    template_name = 'edit_task.html'
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
            messages.error(request, 'You do not have permission to edit this task.')
            return redirect('tasks')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Update the task and show success message"""
        messages.success(self.request, 'Your task has been updated successfully!')
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
    template_name = 'edit_appointment.html'
    pk_url_kwarg = 'pk'
    login_url = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Check permissions before processing request"""
        obj = self.get_object()
        if obj.created_by != request.user:
            messages.error(request, 'You do not have permission to edit this appointment.')
            return redirect('appointments')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Update the appointment and show success message"""
        messages.success(self.request, 'Your appointment has been updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect back to appointments"""
        return reverse_lazy('appointments')


class DeleteForumQuestionView(LoginRequiredMixin, IsAuthorMixin, DeleteView):
    """
    View for deleting a forum question
    Only the author can delete their own question
    """
    model = ForumQuestion
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('forum')
    login_url = reverse_lazy('login')
    
    def delete(self, request, *args, **kwargs):
        """Delete the question and show success message"""
        messages.success(request, 'Your question has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DeleteForumAnswerView(LoginRequiredMixin, IsAuthorMixin, DeleteView):
    """
    View for deleting a forum answer
    Only the author can delete their own answer
    """
    model = ForumAnswer
    pk_url_kwarg = 'answer_id'
    login_url = reverse_lazy('login')
    
    def get_success_url(self):
        """Redirect back to the question"""
        return reverse_lazy('forum_question', kwargs={'slug': self.object.question.slug})
    
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
    success_url = reverse_lazy('blog_feed')
    login_url = reverse_lazy('login')
    
    def delete(self, request, *args, **kwargs):
        """Delete the blog post and show success message"""
        messages.success(request, 'Your blog post has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


