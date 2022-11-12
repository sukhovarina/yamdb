from django.urls import include, path
from rest_framework import routers

from .views import (
    GetJWT, Authenticate, UserViewSet, TitleViewSet,
    CategoryViewSet, GenreViewSet, CommentsViewSet, ReviewsViewSet
)

app_name = 'api'
router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'titles', TitleViewSet, basename='title')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='review'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comment'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', Authenticate.as_view()),
    path('v1/auth/token/', GetJWT.as_view()),
]
