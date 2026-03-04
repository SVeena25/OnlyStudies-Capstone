from django.contrib import admin
from django.contrib import messages
from .models import Category, SubCategory, BlogPost, Notification, ForumQuestion, ForumAnswer, Task, Appointment
from cloudinary.exceptions import Error as CloudinaryError


class SubCategoryInline(admin.TabularInline):
    """
    Inline admin for subcategories
    """
    model = SubCategory
    extra = 1
    fields = ('name', 'slug', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin for Category model
    """
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]
    search_fields = ('name', 'description')


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """
    Admin for SubCategory model
    """
    list_display = ('name', 'category', 'slug', 'created_at')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'category__name')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Admin for BlogPost model
    """
    list_display = ('title', 'author', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fields = ('title', 'slug', 'author', 'category', 'content', 'featured_image', 'is_published')
    
    def get_fields(self, request, obj=None):
        """
        Show timestamps only when editing
        """
        fields = list(super().get_fields(request, obj))
        if obj:  # Editing existing object
            fields.extend(['created_at', 'updated_at'])
        return fields

    def save_model(self, request, obj, form, change):
        original_image = None
        if change:
            try:
                original_image = BlogPost.objects.only('featured_image').get(pk=obj.pk).featured_image
            except BlogPost.DoesNotExist:
                original_image = None

        try:
            super().save_model(request, obj, form, change)
        except CloudinaryError:
            obj.featured_image = original_image
            obj.save()
            self.message_user(
                request,
                'Post details were saved, but image upload failed. Please verify Cloudinary credentials.',
                level=messages.WARNING,
            )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin for Notification model
    """
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Links', {
            'fields': ('related_url',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    readonly_fields = ('created_at',)


class ForumAnswerInline(admin.TabularInline):
    """
    Inline admin for forum answers
    """
    model = ForumAnswer
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'content', 'is_accepted', 'created_at')


@admin.register(ForumQuestion)
class ForumQuestionAdmin(admin.ModelAdmin):
    """
    Admin for ForumQuestion model
    """
    list_display = ('title', 'author', 'category', 'is_answered', 'views', 'created_at')
    list_filter = ('is_answered', 'category', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('slug', 'views', 'created_at', 'updated_at')
    inlines = [ForumAnswerInline]
    
    fieldsets = (
        ('Question Information', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Status', {
            'fields': ('is_answered', 'views')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ForumAnswer)
class ForumAnswerAdmin(admin.ModelAdmin):
    """
    Admin for ForumAnswer model
    """
    list_display = ('question', 'author', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('content', 'author__username', 'question__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Answer Information', {
            'fields': ('question', 'author', 'is_accepted')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin for Task model
    """
    list_display = ('title', 'created_by', 'category', 'priority', 'due_date', 'created_at')
    list_filter = ('priority', 'category', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at',)
    fields = ('title', 'description', 'category', 'priority', 'due_date', 'created_by')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Admin for Appointment model
    """
    list_display = ('title', 'created_by', 'appointment_datetime', 'created_at')
    list_filter = ('appointment_datetime', 'created_at')
    search_fields = ('title', 'notes', 'created_by__username')
    readonly_fields = ('created_at',)
    fields = ('title', 'notes', 'appointment_datetime', 'created_by')


