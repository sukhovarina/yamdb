from rest_framework import status, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.core.mail import send_mail
from random import randint
from reviews.models import Category, Genre, Title, Review
from users.models import User
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import (
    AdminOnly, AdminOrReadOnly,
    AuthorOrReadOnly, ModeratorOrReadOnly
)
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import TitleFilter
from users.serializers import (
    AuthSerializer, JWTSerializer,
    AdminSerializer
)
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    TitleUpdateSerializer, CommentSerializer, ReviewSerializer
)


class Authenticate(APIView):
    def post(self, request):
        try:
            user = User.objects.get(
                username=request.data['username'],
                email=request.data['email']
            )
            serializer = AuthSerializer(user, data=request.data)
        except Exception:
            serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = str(randint(100000, 999999))
        serializer.save(confirmation_code=code)
        data = serializer.validated_data
        user = User.objects.get(username=data['username'])
        send_mail(
            'Код для регистрации',
            f'Ваш код: {code}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetJWT(APIView):
    def post(self, request):
        serializer = JWTSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])
        if data['confirmation_code'] == user.confirmation_code:
            refresh = RefreshToken.for_user(user).access_token
            return Response(
                {'token': str(refresh)},
                status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Неверный код'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (AdminOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid()
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()


class BaseCategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AdminOrReadOnly,)
    lookup_field = 'slug'


class CategoryViewSet(BaseCategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def perform_create(self, serializer):
        serializer.save()


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title
        .objects
        .select_related('category')
        .annotate(rating=Avg('reviews__score'))
    )
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        if (self.action == 'create'
                or self.action == 'partial_update'):
            return TitleUpdateSerializer
        return TitleSerializer


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        AdminOrReadOnly | ModeratorOrReadOnly
        | (AuthorOrReadOnly & IsAuthenticated)
    ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        AdminOrReadOnly | ModeratorOrReadOnly
        | (AuthorOrReadOnly & IsAuthenticated)
    ]
    pegination_class = PageNumberPagination

    def get_title(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(title=self.get_title(), author=self.request.user)
