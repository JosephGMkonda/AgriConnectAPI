from django.urls import path
from . import views

urlpatterns = [
    path('users', views.list_users, name='list_users'),
    path('create', views.create_user, name='create_user'),
    path('users/<int:pk>/', views.retrieve_user, name='retrieve_user'),
]