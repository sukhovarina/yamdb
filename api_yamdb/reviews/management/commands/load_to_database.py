import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import (
    Category, Genre, GenreTitle, Title, Comment, Reviews, User
)

DICT = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Reviews: 'review.csv',
    Comment: 'comments.csv',
    GenreTitle: 'genre_title.csv'
}


class Command(BaseCommand):

    def handle(self, *args, **options):
        for model, base in DICT.items():
            with open(
                    f'{settings.BASE_DIR}/static/data/{base}',
                    'r', encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(model(**data) for data in reader)

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
