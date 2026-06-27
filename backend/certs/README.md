JWT RSA keys for RS256 signing.

| File | Purpose |
|------|---------|
| `private.pem` | Signs tokens (encode) — **do not commit** |
| `public.pem` | Verifies tokens (decode) |

Loaded by `core/jwt.py` (bolapi-style, local certs instead of S3).

Default paths:
- `backend/certs/private.pem`
- `backend/certs/public.pem`

Override with env vars:
- `LOCAL_PRIVATE_PEM_FILE`
- `LOCAL_PUBLIC_PEM_FILE`
- `PEM_FILE_PWD` (if private key is password-protected)

Generate keys:

```bash
./scripts/generate_jwt_keys.sh
```
