from rest_framework.routers import DefaultRouter
from .views import FollowViewSet

router = DefaultRouter()
router.register(r"Follow", FollowViewSet, basename="Follow")

urlpatterns = router.urls