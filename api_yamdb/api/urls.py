from django.urls import include, path

from rest_framework import routers

from .views import TitleViewSet, CategoryViewSet, GenreViewSet


app_name = 'api'
router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'titles', TitleViewSet, basename='title')

urlpatterns = [
    path('v1/', include(router.urls)),
    ]
