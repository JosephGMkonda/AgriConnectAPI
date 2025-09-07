from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.get_user_profile, name='get_own_profile'),
    path('profile/update/', views.update_user_profile, name='update_profile'),
    path('profile/<int:user_id>/', views.get_user_profile, name='get_user_profile'),
    path('profiles/search/', views.search_profile, name='search_profile'),
]