#!/usr/bin/env bash

set -euo pipefail

# --------------------------------------------------
# SIMServe Server Certificate Generator
# --------------------------------------------------

if [[ $# -ne 3 ]]; then
    echo "Usage:"
    echo "  $0 <ca.key> <ca.crt> <server_ip>"
    echo
    echo "Example:"
    echo "  $0 ./certs/ca/ca.key ./certs/ca/ca.crt 1.2.3.4"
    exit 1
fi

CA_KEY="$1"
CA_CERT="$2"
SERVER_IP="$3"

# Resolve project root from this script's location:
#   sim_server/tools/generate-server-cert.sh
#                 ↑
#             project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

OUTPUT_DIR="$PROJECT_ROOT/src/simserver/certs"

SERVER_KEY="$OUTPUT_DIR/server.key"
SERVER_CSR="$OUTPUT_DIR/server.csr"
SERVER_CERT="$OUTPUT_DIR/server.crt"
SERVER_CNF="$OUTPUT_DIR/server.cnf"

echo "[*] Checking inputs..."

if [[ ! -f "$CA_KEY" ]]; then
    echo "[!] CA private key not found:"
    echo "    $CA_KEY"
    exit 1
fi

if [[ ! -f "$CA_CERT" ]]; then
    echo "[!] CA certificate not found:"
    echo "    $CA_CERT"
    exit 1
fi

if [[ -z "$SERVER_IP" ]]; then
    echo "[!] Server IP is empty."
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "[*] Output directory:"
echo "    $OUTPUT_DIR"
echo

echo "[*] Generating server private key..."

openssl genrsa \
    -out "$SERVER_KEY" \
    2048

echo "[*] Creating OpenSSL configuration..."

cat > "$SERVER_CNF" <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = SIMServe Server

[v3_req]
subjectAltName = IP:$SERVER_IP
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
EOF

echo "[*] Generating CSR..."

openssl req \
    -new \
    -key "$SERVER_KEY" \
    -out "$SERVER_CSR" \
    -config "$SERVER_CNF"

echo "[*] Signing certificate with SIMServe Root CA..."

openssl x509 \
    -req \
    -in "$SERVER_CSR" \
    -CA "$CA_CERT" \
    -CAkey "$CA_KEY" \
    -CAcreateserial \
    -out "$SERVER_CERT" \
    -days 825 \
    -sha256 \
    -extfile "$SERVER_CNF" \
    -extensions v3_req

echo
echo "========================================"
echo " SIMServe Server Certificate Generated"
echo "========================================"
echo
echo "Server IP:"
echo "    $SERVER_IP"
echo
echo "Generated files:"
echo "    Private Key : $SERVER_KEY"
echo "    Certificate : $SERVER_CERT"
echo "    CSR         : $SERVER_CSR"
echo "    Config      : $SERVER_CNF"
echo
echo "IMPORTANT:"
echo "    Keep server.key private."
echo "    Restart SIMServe server to load the new certificate."
echo