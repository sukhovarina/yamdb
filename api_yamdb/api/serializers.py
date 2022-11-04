from rest_framework import serializers

from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField()
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        read_only_fields = (
            'id', 'name', 'year', 'description', 'rating','genre', 'category'
        )


class TitleUpdateSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)
    category = serializers.SlugField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'rating', 'year', 'description', 'genre', 'category'
        )
