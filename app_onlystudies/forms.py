from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import ForumQuestion, ForumAnswer


class SignUpForm(forms.ModelForm):
    """
    Custom signup form with password validation and security
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        }),
        help_text="Password must be at least 8 characters long and contain uppercase, lowercase, and numbers."
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
            raise ValidationError("Username must be at least 3 characters long.")
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
        user.set_password(password)
        if commit:
            user.save()
        return user


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
            raise ValidationError("Question title must be at least 10 characters long.")
        return title

    def clean_content(self):
        """Validate content"""
        content = self.cleaned_data.get('content')
        if len(content) < 20:
            raise ValidationError("Question content must be at least 20 characters long.")
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
            raise ValidationError("Answer must be at least 10 characters long.")
        return content
