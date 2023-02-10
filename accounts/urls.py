from rest_framework.routers import DefaultRouter

from .views import UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="account")
urlpatterns = router.urls
