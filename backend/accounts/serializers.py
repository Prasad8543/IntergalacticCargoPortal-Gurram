from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from core.constants import MESSAGES
from core.validators import CustomPasswordValidator

from .models import Role, User

_password_validator = CustomPasswordValidator()


class UserSerializer(serializers.ModelSerializer):
    """Public user fields only — is_staff and is_superuser are never exposed."""

    role = serializers.SerializerMethodField(
        help_text='Access level: Admin or Standard (assigned at signup from email domain).',
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'mobile')
        read_only_fields = fields

    def get_role(self, obj):
        return obj.access_level


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        help_text=_password_validator.get_help_text(),
    )
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        help_text='Optional given name for the user.',
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        help_text='Optional family name for the user.',
    )
    mobile = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
        help_text='Optional contact number for the user.',
    )
    email = serializers.EmailField(
        help_text=(
            'Unique email for the new account. '
            '@nebula-corp.com addresses are provisioned as Admin; others as Standard.'
        ),
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'mobile')

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                ErrorDetail(string=MESSAGES['user_already_exists'], code='user_already_exists')
            )
        return email

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        user = User(
            email=email,
            first_name=attrs.get('first_name', ''),
            last_name=attrs.get('last_name', ''),
        )
        try:
            validate_password(attrs['password'], user=user)
        except DjangoValidationError as exc:
            message = exc.messages[0] if exc.messages else MESSAGES['password_not_valid'].format(
                settings.PASSWORD_MIN_LENGTH,
                settings.PASSWORD_MAX_LENGTH,
            )
            code = 'password_not_valid'
            if exc.error_list and exc.error_list[0].code:
                code = exc.error_list[0].code
            raise serializers.ValidationError(
                {'password': [ErrorDetail(string=message, code=code)]}
            ) from exc
        return attrs

    def create(self, validated_data):
        mobile = validated_data.pop('mobile', '')
        email = validated_data['email'].strip().lower()
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        role = Role.for_email(email)

        return User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            mobile=mobile,
            role=role,
        )

    def to_representation(self, instance):
        return UserSerializer(instance).data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text='Registered email address (case-insensitive).',
    )
    password = serializers.CharField(
        write_only=True,
        help_text='Account password.',
    )
