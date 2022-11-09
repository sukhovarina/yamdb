from django.urls import include, path

from rest_framework import routers

from .views import TitleViewSet, CategoryViewSet, GenreViewSet, CommentsViewSet, ReviewsViewSet


app_name = 'api'
router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'titles', TitleViewSet, basename='title')
router.register(r'reviews', ReviewsViewSet, basename='reviews')
router.register(
    r'posts/(?P<post_id>\d+)/comments',
    CommentsViewSet,
    basename=r'posts/(?P<post_id>\d+)/comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    ]
