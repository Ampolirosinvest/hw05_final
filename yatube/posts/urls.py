from django.urls import path
from . import views


app_name = 'posts'  # обьявил namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    #  Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    #  Просмотр записи
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    #  Создание записи
    path('create/', views.post_create, name='post_create'),
    path('posts/<post_id>/edit/', views.post_edit, name='post_edit'),
    # добавление комментария
    path('posts/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    # посты на которые подписан авторизованный клиент
    path('follow/', views.follow_index, name='follow_index'),
    # подписка на пользователя
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'),
    # отписка от пользователя
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'),
]