MESSAGES = {
    'password_not_valid': (
        'Password should contain minimum of {} characters and maximum of {} characters '
        'with atleast one upper case, one lower case and a special character.'
    ),
    'user_already_exists': 'User with this email is already exists.',
}

DEFAULT_ERROR_RESPONSE_FIELDS = {'message', 'code', 'scope'}

SIGNATURE_EXPIRED_MESSAGE = 'Signature has expired'
EXPIRED_SIGNATURE_CODE = 'expired_signature'
