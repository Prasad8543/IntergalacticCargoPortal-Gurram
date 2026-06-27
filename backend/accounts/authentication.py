import jwt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from accounts.models import User
from core.constants import EXPIRED_SIGNATURE_CODE, SIGNATURE_EXPIRED_MESSAGE
from core.jwt import jwt_decode_handler


class RS256JWTAuthentication(JWTAuthentication):
    """Authenticate requests using JWT signed with local certs (RS256)."""

    def get_raw_token(self, header):
        return super().get_raw_token(header)

    def get_validated_token(self, raw_token):
        try:
            payload = jwt_decode_handler(raw_token)
        except jwt.ExpiredSignatureError as exc:
            raise InvalidToken(
                SIGNATURE_EXPIRED_MESSAGE,
                code=EXPIRED_SIGNATURE_CODE,
            ) from exc
        except Exception as exc:
            raise InvalidToken({'detail': 'Given token not valid for any token type'}) from exc

        if payload.get('token_type') != 'access':
            raise InvalidToken({'detail': 'Token has wrong type'})

        return payload

    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
        except KeyError as exc:
            raise InvalidToken({'detail': 'Token contained no recognizable user identification'}) from exc

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed('User not found', code='user_not_found') from exc

        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        return user
