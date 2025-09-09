from django.urls import path
from . import views

urlpatterns = [
    path('users', views.list_users, name='list_users'),
    path('create/', views.create_user, name='create_user'),
    path('me/', views.get_current_user, name='get_current_user'),
]