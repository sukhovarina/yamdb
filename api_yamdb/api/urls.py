from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GetJWT, Authenticate, UserViewSet

app_name = 'api'
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', Authenticate.as_view()),
    path('v1/auth/token/', GetJWT.as_view()),
]
