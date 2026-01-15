from django.contrib import admin
from .models import Category, SubCategory, BlogPost, Notification, ForumQuestion, ForumAnswer


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


