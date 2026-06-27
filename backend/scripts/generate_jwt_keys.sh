#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="$DIR/../certs"

mkdir -p "$CERTS_DIR"
openssl genrsa -out "$CERTS_DIR/private.pem" 2048
openssl rsa -in "$CERTS_DIR/private.pem" -pubout -out "$CERTS_DIR/public.pem"

echo "Generated:"
echo "  $CERTS_DIR/private.pem  (sign tokens — keep secret, not committed)"
echo "  $CERTS_DIR/public.pem   (verify tokens)"
