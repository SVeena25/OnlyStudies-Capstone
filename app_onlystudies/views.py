from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from .forms import SignUpForm, ForumQuestionForm, ForumAnswerForm
from .models import Category, SubCategory, BlogPost, Notification, ForumQuestion, ForumAnswer


class HomePage(TemplateView):
    """
    Displays home page
    """
    template_name = 'index.html'


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
        login(self.request, user)
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
        blog_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:200],  # First 200 characters
            'author': post.author.get_full_name() or post.author.username,
            'category': post.category.name if post.category else 'General',
            'featured_image': post.featured_image.url if post.featured_image else None,
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
        return JsonResponse({'notifications': [], 'error': 'User not authenticated'}, status=401)
    
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
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

