from . import views
from django.urls import path

urlpatterns = [
    path('', 
        views.HomePage.as_view(), name='home'),
    path('signup/', 
        views.SignUpView.as_view(), name='signup'),
    path('login/', 
        views.CustomLoginView.as_view(), name='login'),
    path('logout/', 
        views.CustomLogoutView.as_view(), name='logout'),
    path('category/<slug:category_slug>/', 
        views.CategoryView.as_view(), name='category'),
    path('category/<slug:category_slug>/<slug:subcategory_slug>/', 
        views.SubCategoryView.as_view(), name='subcategory'),
    
    # Blog Feed
    path('blog/', 
        views.BlogFeedView.as_view(), name='blog_feed'),
    
    # Forum
    path('forum/', 
        views.ForumView.as_view(), name='forum'),
    path('forum/ask/', 
        views.AskQuestionView.as_view(), name='ask_question'),
    path('forum/<slug:slug>/', 
        views.ForumQuestionDetailView.as_view(), name='forum_question'),
    path('forum/<slug:slug>/answer/', 
        views.post_answer, name='post_answer'),
    
    # Exam Application
    path('apply/<str:exam_name>/', 
        views.apply_exam, name='apply_exam'),
    
    # API Endpoints
    path('api/blog-feed/', 
        views.blog_feed_api, name='blog_feed_api'),
    path('api/notifications/', 
        views.notifications_api, name='notifications_api'),
]
