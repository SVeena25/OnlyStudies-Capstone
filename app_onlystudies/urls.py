from . import views
from django.urls import path

urlpatterns = [
    path('', 
        views.HomePage.as_view(), name='home'),
    path('about/', 
        views.AboutView.as_view(), name='about'),
    path('signup/', 
        views.SignUpView.as_view(), name='signup'),
    path('login/', 
        views.CustomLoginView.as_view(), name='login'),
    path('logout/', 
        views.CustomLogoutView.as_view(), name='logout'),
    path('tasks/', 
        views.TaskListView.as_view(), name='tasks'),
    path('tasks/add/',
        views.CreateTaskView.as_view(), name='add_task'),
    path('tasks/<int:pk>/edit/', 
        views.UpdateTaskView.as_view(), name='edit_task'),
    path('tasks/<int:pk>/delete/',
        views.DeleteTaskView.as_view(), name='delete_task'),
    path('appointments/', 
        views.AppointmentListView.as_view(), name='appointments'),
    path('appointments/book/', 
        views.AppointmentCreateView.as_view(), name='book_appointment'),
    path('appointments/<int:pk>/edit/', 
        views.UpdateAppointmentView.as_view(), name='edit_appointment'),
    path('search/', 
        views.SearchResultsView.as_view(), name='search'),
    path('category/<slug:category_slug>/', 
        views.CategoryView.as_view(), name='category'),
    path('category/<slug:category_slug>/<slug:subcategory_slug>/', 
        views.SubCategoryView.as_view(), name='subcategory'),
    
    # Blog
    path('blog/<slug:slug>/', 
        views.BlogPostDetailView.as_view(), name='blog_detail'),
    path('blog/<slug:slug>/edit/', 
        views.UpdateBlogPostView.as_view(), name='edit_blog'),
    path('blog/<slug:slug>/delete/', 
        views.DeleteBlogPostView.as_view(), name='delete_blog'),

    # Notifications
    path('notifications/', 
        views.NotificationsView.as_view(), name='notifications'),
    
    # Forum
    path('forum/', 
        views.ForumView.as_view(), name='forum'),
    path('forum/ask/', 
        views.AskQuestionView.as_view(), name='ask_question'),
    path('forum/<slug:slug>/', 
        views.ForumQuestionDetailView.as_view(), name='forum_question'),
    path('forum/<slug:slug>/edit/', 
        views.UpdateForumQuestionView.as_view(), name='edit_question'),
    path('forum/<slug:slug>/delete/', 
        views.DeleteForumQuestionView.as_view(), name='delete_question'),
    path('forum/<slug:slug>/answer/', 
        views.post_answer, name='post_answer'),
    path('forum/<slug:slug>/answer/<int:answer_id>/edit/', 
        views.UpdateForumAnswerView.as_view(), name='edit_answer'),
    path('forum/<slug:slug>/answer/<int:answer_id>/delete/', 
        views.DeleteForumAnswerView.as_view(), name='delete_answer'),
    
    # Exam Application
    path('apply/<str:exam_name>/', 
        views.apply_exam, name='apply_exam'),
    
    # API Endpoints
    path('api/blog-feed/', 
        views.blog_feed_api, name='blog_feed_api'),
    path('api/notifications/', 
        views.notifications_api, name='notifications_api'),
]
