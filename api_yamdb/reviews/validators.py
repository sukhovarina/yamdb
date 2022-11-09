import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя me недоступно!')
        )
    if re.search(r'^[\w.@+-]+$', value) is None:
        raise ValidationError(
            (f'Недопустимые символы в имени {value}!')
        )
