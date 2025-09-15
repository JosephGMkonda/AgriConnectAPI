from rest_framework.routers import DefaultRouter
from .views import CommentViewSet

router = DefaultRouter()
router.register(r"Comments", CommentViewSet, basename="Comments")

urlpatterns = router.urls


