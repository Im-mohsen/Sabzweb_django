from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path('', views.index, name="index"),
    # path('posts/', views.post_list, name="post_list"),
    path('posts/', views.PostListView.as_view(), name="post_list"),
    path('posts/<pk>', views.post_detail, name="post_detail"),
    path('posts/<post_id>/comment', views.post_comment, name="post_comment"),
    # path('posts/<pk>', views.PostDetailView.as_view(), name="post_detail"),
    path('ticket/', views.ticket, name="ticket"),
    path('create-post/', views.create_post, name="New_post"),
    path('search/', views.post_search, name="post_search"),
    path('profile/', views.profile, name="profile"),
]