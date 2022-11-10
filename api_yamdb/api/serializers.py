from rest_framework import serializers
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Title, Reviews, Users


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class JWTSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField()
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        read_only_fields = (
            'id', 'name', 'year', 'description', 'rating', 'genre', 'category'
        )


class TitleUpdateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'rating', 'year', 'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Reviews
        read_only_fields = ('title',)

    def validate_score(self, value):
        if not (0 < value <= 10):
            raise serializers.ValidationError(
                'Рейтинг должен быть целым числом от 0 до 10!'
            )
        return value

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context.get('request').user
        title = get_object_or_404(Title, pk=title_id)
        if (title.reviews.filter(author=author).exists()
            and self.context.get('request').method != 'PATCH'):
            raise serializers.ValidationError(
                'На одно произведение можно оставлять только один отзыв!'
            )
        return data
