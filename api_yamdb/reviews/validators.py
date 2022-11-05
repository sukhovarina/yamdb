from datetime import date

from django.core.exceptions import ValidationError


def validate_year(self, value):
    year = date.today().year
    if value >= year:
        raise ValidationError('Укажите правильный год.')
    return value
