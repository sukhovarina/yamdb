from rest_framework import status, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.core.mail import send_mail
from random import randint
from reviews.models import User, Category, Genre, Title, Review
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import AdminOnly, AdminOrReadOnly, AdminModOwnerOrReadOnly
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import TitleFilter
from .serializers import (
    AuthSerializer, JWTSerializer,
    AdminSerializer, CategorySerializer,
    GenreSerializer, TitleSerializer, TitleUpdateSerializer,
    CommentSerializer, ReviewSerializer
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
        if serializer.is_valid():
            code = str(randint(100000, 999999))
            serializer.save(confirmation_code=code)
            data = serializer.validated_data
            user = User.objects.get(username=data['username'])
            send_mail(  # отправляем код на указанную юзером почту
                'Код для регистрации',
                f'Ваш код: {code}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetJWT(APIView):
    def post(self, request):
        serializer = JWTSerializer(data=request.data)
        if serializer.is_valid():
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
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


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
        .select_related()
        .annotate(rating=Avg('reviews__score'))
        .select_related()
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
    permission_classes = (AdminModOwnerOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_review(self):
        return get_object_or_404(
            Review, pk=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        return self.get_review.comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review
        )


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminModOwnerOrReadOnly,)
    pegination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(title=title, author=self.request.user)
