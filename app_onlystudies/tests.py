from django.test import TestCase, Client
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from app_onlystudies.models import (
    Category,
    SubCategory,
    BlogPost,
    BlogComment,
    BlogPostVote,
    Notification,
    Task,
    ForumQuestion,
    ForumAnswer,
    Appointment,
)
import json


class AuthenticationTest(TestCase):
    """Test cases for authentication views (login, logout, welcome)"""
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_login_page_accessible(self):
        """Test login page is accessible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
    
    def test_login_successful(self):
        """Test successful user login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Check if user is authenticated after login POST (redirects to home)
        self.assertEqual(response.status_code, 302)  # Redirect status
        # Verify user is authenticated by checking session
        self.assertIn('_auth_user_id', self.client.session)
    
    def test_login_redirect_to_home(self):
        """Test login redirects authenticated user to home page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('login'))
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
    
    def test_welcome_message_on_home_when_authenticated(self):
        """Test welcome message appears on home page for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # Check for welcome message with user's name or username
        content = response.content.decode()
        self.assertIn('Welcome', content)
        # Should show first name if available, otherwise username
        self.assertTrue('Test' in content or 'testuser' in content)
    
    def test_no_welcome_message_when_not_authenticated(self):
        """Test welcome message doesn't appear for unauthenticated user"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Should show login/signup links instead
        self.assertIn('Login', content)
        self.assertIn('Sign Up', content)
    
    def test_logout_requires_post(self):
        """Test logout requires POST method (not GET)"""
        self.client.login(username='testuser', password='testpass123')
        # GET request should not logout
        response = self.client.get(reverse('logout'), follow=True)
        # Should still be authenticated after GET
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_logout_with_post_successful(self):
        """Test successful logout with POST method"""
        self.client.login(username='testuser', password='testpass123')
        # Verify logged in
        response = self.client.get(reverse('home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
        # Logout with POST
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        # Should be redirected and not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_logout_redirects_to_home(self):
        """Test logout redirects to home page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('home'))
    
    def test_logout_form_has_csrf_token(self):
        """Test logout form includes CSRF token"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        content = response.content.decode()
        # Check for CSRF token in logout form
        self.assertIn('csrfmiddlewaretoken', content)
    
    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        # Should re-render login page with error
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_signup_assigns_student_role_group(self):
        """Test signup assigns selected Student group role."""
        response = self.client.post(reverse('signup'), {
            'first_name': 'Role',
            'last_name': 'Student',
            'username': 'studentroleuser',
            'email': 'studentrole@example.com',
            'role': 'student',
            'password': 'RolePass123!',
            'password_confirm': 'RolePass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='studentroleuser')
        self.assertTrue(user.groups.filter(name='Student').exists())

    def test_login_redirects_instructor_to_create_blog(self):
        """Instructor users should be redirected to create blog page by default."""
        instructor_group, _ = Group.objects.get_or_create(name='Instructor')
        instructor = User.objects.create_user(
            username='instructoruser',
            email='instructor@example.com',
            password='RolePass123!'
        )
        instructor.groups.add(instructor_group)

        response = self.client.post(reverse('login'), {
            'username': 'instructoruser',
            'password': 'RolePass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('create_blog'))


class CategoryModelTest(TestCase):
    """Test cases for Category model"""
    
    def setUp(self):
        """Create a test category"""
        self.category = Category.objects.create(
            name='MBA',
            slug='mba',
            description='Master of Business Administration'
        )
    
    def test_category_creation(self):
        """Test category is created correctly"""
        self.assertEqual(self.category.name, 'MBA')
        self.assertEqual(self.category.slug, 'mba')
    
    def test_category_str_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'MBA')
    
    def test_category_slug_unique(self):
        """Test category slug is unique"""
        with self.assertRaises(Exception):
            Category.objects.create(name='MBA 2', slug='mba')


class SubCategoryModelTest(TestCase):
    """Test cases for SubCategory model"""
    
    def setUp(self):
        """Create test category and subcategory"""
        self.category = Category.objects.create(
            name='Engineering',
            slug='engineering'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='Mechanical',
            slug='mechanical',
            description='Mechanical Engineering'
        )
    
    def test_subcategory_creation(self):
        """Test subcategory is created correctly"""
        self.assertEqual(self.subcategory.name, 'Mechanical')
        self.assertEqual(self.subcategory.category, self.category)
    
    def test_subcategory_str_representation(self):
        """Test subcategory string representation"""
        self.assertEqual(str(self.subcategory), 'Engineering - Mechanical')


class BlogPostModelTest(TestCase):
    """Test cases for BlogPost model"""
    
    def setUp(self):
        """Create test user, category, and blog post"""
        self.user = User.objects.create_user(
            username='testauthor',
            email='author@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Medical',
            slug='medical'
        )
        self.blog_post = BlogPost.objects.create(
            title='Medical Test Article',
            content='This is test content for medical blog post',
            author=self.user,
            category=self.category,
            slug='medical-test-article',
            is_published=True
        )
    
    def test_blog_post_creation(self):
        """Test blog post is created correctly"""
        self.assertEqual(self.blog_post.title, 'Medical Test Article')
        self.assertEqual(self.blog_post.author, self.user)
        self.assertTrue(self.blog_post.is_published)
    
    def test_blog_post_str_representation(self):
        """Test blog post string representation"""
        self.assertEqual(str(self.blog_post), 'Medical Test Article')
    
    def test_blog_post_ordering(self):
        """Test blog posts are ordered by creation date (newest first)"""
        blog1 = BlogPost.objects.create(
            title='First Post',
            content='Content 1',
            author=self.user,
            slug='first-post'
        )
        blog2 = BlogPost.objects.create(
            title='Second Post',
            content='Content 2',
            author=self.user,
            slug='second-post'
        )
        posts = list(BlogPost.objects.all())
        self.assertEqual(posts[0], blog2)  # Most recent first


class NotificationModelTest(TestCase):
    """Test cases for Notification model"""
    
    def setUp(self):
        """Create test user and notification"""
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            notification_type='system',
            is_read=False
        )
    
    def test_notification_creation(self):
        """Test notification is created correctly"""
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertEqual(self.notification.user, self.user)
        self.assertFalse(self.notification.is_read)
    
    def test_notification_str_representation(self):
        """Test notification string representation"""
        self.assertEqual(str(self.notification), 'testuser - Test Notification')
    
    def test_notification_types(self):
        """Test all notification types are valid"""
        types = ['course', 'forum', 'achievement', 'system']
        for notif_type in types:
            notif = Notification.objects.create(
                user=self.user,
                title=f'{notif_type} notification',
                message='Test',
                notification_type=notif_type
            )
            self.assertEqual(notif.notification_type, notif_type)


class BlogFeedAPITest(TestCase):
    """Test cases for blog feed API endpoint"""
    
    def setUp(self):
        """Create test data for API"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testauthor',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        
        # Create 3 published blog posts
        for i in range(3):
            BlogPost.objects.create(
                title=f'Blog Post {i+1}',
                content=f'Content for blog post {i+1}' * 50,
                author=self.user,
                category=self.category,
                slug=f'blog-post-{i+1}',
                is_published=True
            )
        
        # Create 1 unpublished blog post (should not appear in API)
        BlogPost.objects.create(
            title='Unpublished Post',
            content='This should not appear',
            author=self.user,
            slug='unpublished-post',
            is_published=False
        )
    
    def test_blog_feed_api_returns_published_posts(self):
        """Test API returns only published posts"""
        response = self.client.get(reverse('blog_feed_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['blogs']), 3)
    
    def test_blog_feed_api_response_format(self):
        """Test API response has correct format"""
        response = self.client.get(reverse('blog_feed_api'))
        data = json.loads(response.content)
        
        self.assertIn('blogs', data)
        self.assertTrue(len(data['blogs']) > 0)
        
        blog = data['blogs'][0]
        required_fields = ['id', 'title', 'content', 'author', 'category', 'created_at', 'slug']
        for field in required_fields:
            self.assertIn(field, blog)
    
    def test_blog_feed_api_limits_to_five(self):
        """Test API returns maximum 5 posts"""
        # Create 10 more posts
        for i in range(10):
            BlogPost.objects.create(
                title=f'Extra Post {i+1}',
                content='Content',
                author=self.user,
                slug=f'extra-post-{i+1}',
                is_published=True
            )
        
        response = self.client.get(reverse('blog_feed_api'))
        data = json.loads(response.content)
        self.assertLessEqual(len(data['blogs']), 5)


class NotificationsAPITest(TestCase):
    """Test cases for notifications API endpoint"""
    
    def setUp(self):
        """Create test data for API"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        
        # Create notifications for test user
        for i in range(3):
            Notification.objects.create(
                user=self.user,
                title=f'Notification {i+1}',
                message=f'Message {i+1}',
                notification_type='system',
                is_read=False
            )
        
        # Create read notification (should not appear)
        Notification.objects.create(
            user=self.user,
            title='Read Notification',
            message='Already read',
            notification_type='system',
            is_read=True
        )
        
        # Create notification for other user (should not appear)
        Notification.objects.create(
            user=self.other_user,
            title='Other User Notification',
            message='Not for test user',
            notification_type='system',
            is_read=False
        )
    
    def test_notifications_api_requires_authentication(self):
        """Test API returns 401 for unauthenticated user"""
        response = self.client.get(reverse('notifications_api'))
        self.assertEqual(response.status_code, 401)
    
    def test_notifications_api_returns_unread_only(self):
        """Test API returns only unread notifications"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['notifications']), 3)
    
    def test_notifications_api_user_isolation(self):
        """Test users only see their own notifications"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications_api'))
        data = json.loads(response.content)
        
        # Should only see notifications for logged-in user
        for notif in data['notifications']:
            self.assertNotEqual(notif['title'], 'Other User Notification')
    
    def test_notifications_api_response_format(self):
        """Test API response has correct format"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications_api'))
        data = json.loads(response.content)
        
        self.assertIn('notifications', data)
        if len(data['notifications']) > 0:
            notif = data['notifications'][0]
            required_fields = ['id', 'title', 'message', 'type', 'is_read', 'created_at']
            for field in required_fields:
                self.assertIn(field, notif)


class TaskCRUDTest(TestCase):
    """Frontend Task CRUD tests for regular authenticated users"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='taskuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Task Cat', slug='task-cat')
        self.client.login(username='taskuser', password='testpass123')

    def test_create_task_from_frontend(self):
        response = self.client.post(reverse('add_task'), {
            'title': 'Prepare notes',
            'description': 'Prepare module notes',
            'category': self.category.id,
            'priority': 'high',
            'due_date': ''
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='Prepare notes', created_by=self.user).exists())

    def test_update_task_from_frontend(self):
        task = Task.objects.create(
            title='Old task title',
            description='Old desc',
            category=self.category,
            priority='medium',
            created_by=self.user,
        )
        response = self.client.post(reverse('edit_task', kwargs={'pk': task.pk}), {
            'title': 'Updated task title',
            'description': 'Updated desc',
            'category': self.category.id,
            'priority': 'low',
            'due_date': ''
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated task title')

    def test_delete_task_from_frontend(self):
        task = Task.objects.create(
            title='Task to delete',
            priority='medium',
            created_by=self.user,
        )
        response = self.client.post(reverse('delete_task', kwargs={'pk': task.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())


class AppointmentCRUDTest(TestCase):
    """Frontend appointment CRUD tests for authenticated users."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='apptuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otherappt', password='testpass123')
        self.client.login(username='apptuser', password='testpass123')

    def test_create_appointment_from_frontend(self):
        response = self.client.post(reverse('book_appointment'), {
            'title': 'Counseling Session',
            'appointment_datetime': '2099-12-31T10:00',
            'notes': 'Bring required documents',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Appointment.objects.filter(title='Counseling Session', created_by=self.user).exists())

    def test_update_appointment_from_frontend(self):
        appointment = Appointment.objects.create(
            title='Initial Appointment',
            appointment_datetime=timezone.now() + timedelta(days=10),
            notes='Initial notes',
            created_by=self.user,
        )
        response = self.client.post(reverse('edit_appointment', kwargs={'pk': appointment.pk}), {
            'title': 'Updated Appointment',
            'appointment_datetime': '2099-12-31T11:30',
            'notes': 'Updated notes',
        })
        self.assertEqual(response.status_code, 302)
        appointment.refresh_from_db()
        self.assertEqual(appointment.title, 'Updated Appointment')

    def test_delete_appointment_from_frontend(self):
        appointment = Appointment.objects.create(
            title='Appointment to Delete',
            appointment_datetime=timezone.now() + timedelta(days=10),
            created_by=self.user,
        )
        response = self.client.post(reverse('delete_appointment', kwargs={'pk': appointment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Appointment.objects.filter(pk=appointment.pk).exists())

    def test_cannot_delete_other_users_appointment(self):
        appointment = Appointment.objects.create(
            title='Protected Appointment',
            appointment_datetime=timezone.now() + timedelta(days=10),
            created_by=self.other_user,
        )
        response = self.client.post(reverse('delete_appointment', kwargs={'pk': appointment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Appointment.objects.filter(pk=appointment.pk).exists())


class BlogNewsFlowTest(TestCase):
    """Tests for role-restricted news flow and blog comments."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='writer', password='testpass123')
        self.staff_user = User.objects.create_user(username='editor', password='testpass123', is_staff=True)
        self.instructor_user = User.objects.create_user(username='instructor', password='testpass123')
        instructor_group, _ = Group.objects.get_or_create(name='Instructor')
        self.instructor_user.groups.add(instructor_group)
        self.category = Category.objects.create(name='News', slug='news')
        self.post = BlogPost.objects.create(
            title='Published Story',
            content='A' * 80,
            author=self.staff_user,
            category=self.category,
            slug='published-story',
            is_published=True,
        )

    def test_create_news_requires_login(self):
        response = self.client.get(reverse('create_blog'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_non_role_user_cannot_create_news(self):
        self.client.login(username='writer', password='testpass123')
        response = self.client.post(reverse('create_blog'), {
            'title': 'Community News Story',
            'content': 'B' * 100,
            'category': self.category.id,
            'is_published': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        self.assertFalse(BlogPost.objects.filter(title='Community News Story').exists())

    def test_instructor_can_create_news(self):
        self.client.login(username='instructor', password='testpass123')
        response = self.client.post(reverse('create_blog'), {
            'title': 'Instructor News Story',
            'content': 'B' * 100,
            'category': self.category.id,
            'is_published': True,
        })
        self.assertEqual(response.status_code, 302)
        created = BlogPost.objects.get(title='Instructor News Story')
        self.assertEqual(created.author, self.instructor_user)
        self.assertFalse(created.is_published)

    def test_post_comment_creates_blog_comment(self):
        self.client.login(username='writer', password='testpass123')
        response = self.client.post(
            reverse('post_blog_comment', kwargs={'slug': self.post.slug}),
            {'content': 'Great article and very helpful.'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            BlogComment.objects.filter(blog_post=self.post, author=self.user, content='Great article and very helpful.').exists()
        )

    def test_upvote_creates_vote(self):
        self.client.login(username='writer', password='testpass123')
        response = self.client.post(reverse('vote_blog_post', kwargs={'slug': self.post.slug, 'vote_type': 'up'}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BlogPostVote.objects.filter(blog_post=self.post, user=self.user, value=1).exists())

    def test_repeating_same_vote_removes_vote(self):
        self.client.login(username='writer', password='testpass123')
        self.client.post(reverse('vote_blog_post', kwargs={'slug': self.post.slug, 'vote_type': 'up'}))
        self.client.post(reverse('vote_blog_post', kwargs={'slug': self.post.slug, 'vote_type': 'up'}))
        self.assertFalse(BlogPostVote.objects.filter(blog_post=self.post, user=self.user).exists())

    def test_switch_vote_updates_value(self):
        self.client.login(username='writer', password='testpass123')
        self.client.post(reverse('vote_blog_post', kwargs={'slug': self.post.slug, 'vote_type': 'up'}))
        self.client.post(reverse('vote_blog_post', kwargs={'slug': self.post.slug, 'vote_type': 'down'}))
        vote = BlogPostVote.objects.get(blog_post=self.post, user=self.user)
        self.assertEqual(vote.value, -1)


class DatabaseHardeningConstraintsTest(TestCase):
    """Tests for DB-level integrity constraints and appointment validation."""

    def setUp(self):
        self.user = User.objects.create_user(username='dbuser', password='testpass123')
        self.category = Category.objects.create(name='Database', slug='database')
        self.blog_post = BlogPost.objects.create(
            title='DB Integrity Story',
            content='C' * 120,
            author=self.user,
            category=self.category,
            slug='db-integrity-story',
            is_published=True,
        )
        self.question = ForumQuestion.objects.create(
            title='How to normalize data?',
            content='Need help with normalization strategy.',
            author=self.user,
            category=self.category,
        )

    def test_blog_vote_value_check_constraint(self):
        with self.assertRaises(IntegrityError):
            BlogPostVote.objects.create(blog_post=self.blog_post, user=self.user, value=0)

    def test_only_one_accepted_answer_per_question(self):
        ForumAnswer.objects.create(
            question=self.question,
            content='First accepted answer',
            author=self.user,
            is_accepted=True,
        )

        with self.assertRaises(IntegrityError):
            ForumAnswer.objects.create(
                question=self.question,
                content='Second accepted answer',
                author=self.user,
                is_accepted=True,
            )

    def test_appointment_must_be_in_future_validation(self):
        appointment = Appointment(
            title='Past appointment',
            notes='Invalid because it is in the past',
            appointment_datetime=timezone.now() - timedelta(hours=2),
            created_by=self.user,
        )

        with self.assertRaises(ValidationError):
            appointment.full_clean()



