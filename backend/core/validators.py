import re

from django.conf import settings
from django.core.exceptions import ValidationError

from core.constants import MESSAGES

UPPERCASE_PATTERN = re.compile(r'[A-Z]')
LOWERCASE_PATTERN = re.compile(r'[a-z]')
SPECIAL_CHARACTER_PATTERN = re.compile(r'[^\w\s]')


class CustomPasswordValidator:
    """Validate password length and character rules from settings."""

    def __init__(self, min_length=None, max_length=None):
        self.min_length = min_length
        self.max_length = max_length

    def _min_length(self):
        if self.min_length is not None:
            return self.min_length
        return settings.PASSWORD_MIN_LENGTH

    def _max_length(self):
        if self.max_length is not None:
            return self.max_length
        return settings.PASSWORD_MAX_LENGTH

    def _error_message(self):
        return MESSAGES['password_not_valid'].format(
            self._min_length(),
            self._max_length(),
        )

    def validate(self, password, user=None):
        min_length = self._min_length()
        max_length = self._max_length()

        if not (min_length <= len(password) <= max_length):
            raise ValidationError(self._error_message(), code='password_not_valid')

        if not UPPERCASE_PATTERN.search(password):
            raise ValidationError(self._error_message(), code='password_not_valid')

        if not LOWERCASE_PATTERN.search(password):
            raise ValidationError(self._error_message(), code='password_not_valid')

        if not SPECIAL_CHARACTER_PATTERN.search(password):
            raise ValidationError(self._error_message(), code='password_not_valid')

    def get_help_text(self):
        return self._error_message()
