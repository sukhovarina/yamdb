from rest_framework import serializers

from reviews.models import (
    Category, Genre, Title, Review, Comment
)


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
        fields = '__all__'
        read_only_fields = (
            'id', 'name', 'year', 'description',
            'rating', 'genre', 'category'
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
            'id', 'name', 'rating', 'year',
            'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate_score(self, value):
        """Валидация для оценки рейтинга"""
        if not (0 < value <= 10):
            raise serializers.ValidationError(
                'Рейтинг должен быть целым числом от 0 до 10.'
            )
        return value

    def validate(self, data):
        """Валидация для отзывов и оценок"""
        if self.context['request'].method != 'POST':
            return data

        author = self.context['request'].user
        title_id = (self.context['request'].
                    parser_context['kwargs']['title_id']
                    )

        if Review.objects.filter(
                author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Может существовать только один отзыв!'
            )
        return data

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comment
