from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, TagViewSet

router = DefaultRouter()

router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)
