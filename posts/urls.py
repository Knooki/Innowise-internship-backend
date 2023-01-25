from .views import TagViewSet, PageViewSet, PostViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"pages", PageViewSet, basename="page")
router.register(r"posts", PostViewSet, basename="post")
urlpatterns = router.urls
