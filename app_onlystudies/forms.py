from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import (
    ForumQuestion,
    ForumAnswer,
    Appointment,
    BlogPost,
    BlogComment,
    Task,
)


def sanitize_cloudinary_image_link(value):
    """Validate Cloudinary import URL and reject concatenated URLs."""
    cleaned = (value or '').strip()
    if not cleaned:
        return ''

    first_http = cleaned.find('http://')
    first_https = cleaned.find('https://')
    starts_with_url = cleaned.startswith(
        'http://') or cleaned.startswith('https://')

    if not starts_with_url:
        raise ValidationError(
            'Please enter a valid URL starting with http:// or https://.')

    # Detect accidental concatenation such as ...jpghttps://example.com
    second_http = cleaned.find('http://', 7)
    second_https = cleaned.find('https://', 8)
    if second_http != -1 or second_https != -1:
        raise ValidationError(
            (
                'Please provide only one image URL. It looks like multiple '
                'URLs were pasted together.'
            ))

    # Avoid common copy/paste issue where extra text is appended after the URL.
    if ' ' in cleaned or '\n' in cleaned or '\r' in cleaned:
        raise ValidationError(
            (
                'Cloudinary Image Link must contain only one URL with no '
                'extra text.'
            ))

    return cleaned


class SignUpForm(forms.ModelForm):
    """
    Custom signup form with password validation and security
    """
    ROLE_STUDENT = 'student'
    ROLE_INSTRUCTOR = 'instructor'
    ROLE_CHOICES = (
        (ROLE_STUDENT, 'Student'),
        (ROLE_INSTRUCTOR, 'Instructor'),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial=ROLE_STUDENT,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True,
        }),
        help_text='Choose how you will use the platform.',
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        }),
        help_text=(
            'Password must be at least 8 characters long and contain '
            'uppercase, lowercase, and numbers.'
        )
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'required': True
        }),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'required': True
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'required': True
            })
        }

    def clean_username(self):
        """Validate username uniqueness and format"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        if len(username) < 3:
            raise ValidationError(
                "Username must be at least 3 characters long.")
        return username

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password

    def clean(self):
        """Validate password confirmation"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        """Save user with hashed password"""
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        selected_role = self.cleaned_data.get('role', self.ROLE_STUDENT)
        user.set_password(password)
        if commit:
            user.save()
            group_name = (
                'Instructor'
                if selected_role == self.ROLE_INSTRUCTOR
                else 'Student'
            )
            role_group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(role_group)
        return user

    def get_selected_role(self):
        """Return selected role value from cleaned form data."""
        return self.cleaned_data.get('role', self.ROLE_STUDENT)


class ForumQuestionForm(forms.ModelForm):
    """
    Form for creating forum questions
    """
    class Meta:
        model = ForumQuestion
        fields = ('title', 'content', 'category')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your question title',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your question in detail...',
                'rows': 6,
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_title(self):
        """Validate title"""
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise ValidationError(
                "Question title must be at least 10 characters long.")
        return title

    def clean_content(self):
        """Validate content"""
        content = self.cleaned_data.get('content')
        if len(content) < 20:
            raise ValidationError(
                "Question content must be at least 20 characters long.")
        return content


class ForumAnswerForm(forms.ModelForm):
    """
    Form for answering forum questions
    """
    class Meta:
        model = ForumAnswer
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your answer here...',
                'rows': 5,
                'required': True
            })
        }

    def clean_content(self):
        """Validate content"""
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise ValidationError(
                "Answer must be at least 10 characters long.")
        return content


class AppointmentForm(forms.ModelForm):
    """
    Form for booking appointments/events/services at a specific date and time.
    """
    class Meta:
        model = Appointment
        fields = ('title', 'notes', 'appointment_datetime')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Appointment title (e.g., Counseling Session)',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional details...',
                'rows': 4
            }),
            'appointment_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            })
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise ValidationError('Title must be at least 3 characters long.')
        return title


class BlogPostForm(forms.ModelForm):
    """
    Form for creating and updating blog posts
    """
    cloudinary_image_link = forms.URLField(
        required=False,
        label='Cloudinary Image Link',
        help_text='Paste a public image URL to import into Cloudinary.',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/image.jpg'
        })
    )

    class Meta:
        model = BlogPost
        fields = ('title', 'content', 'category', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter blog post title',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your blog post here...',
                'rows': 8,
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_title(self):
        """Validate title"""
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError(
                "Blog post title must be at least 5 characters long.")
        return title

    def clean_content(self):
        """Validate content"""
        content = self.cleaned_data.get('content')
        if len(content) < 50:
            raise ValidationError(
                "Blog post content must be at least 50 characters long.")
        return content

    def clean_cloudinary_image_link(self):
        return sanitize_cloudinary_image_link(
            self.cleaned_data.get('cloudinary_image_link'))


class BlogCommentForm(forms.ModelForm):
    """
    Form for posting comments on blog/news stories.
    """
    class Meta:
        model = BlogComment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts about this story...',
                'rows': 4,
                'required': True
            })
        }

    def clean_content(self):
        content = (self.cleaned_data.get('content') or '').strip()
        if len(content) < 3:
            raise ValidationError(
                'Comment must be at least 3 characters long.')
        return content


class TaskForm(forms.ModelForm):
    """
    Form for creating and updating tasks
    """
    class Meta:
        model = Task
        fields = ('title', 'description', 'category', 'priority', 'due_date')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Task title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Task description (optional)',
                'rows': 4
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }

    def clean_title(self):
        """Validate title"""
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise ValidationError(
                "Task title must be at least 3 characters long.")
        return title
