#!/usr/bin/env bash
# Provisions the "banking" realm, a "banking-ui" client, and a demo user
# in the Keycloak container started by docker-compose.yml. Safe to re-run
# (skips anything that already exists).
set -euo pipefail

KC_URL="http://localhost:8080"
REALM="banking"
CLIENT_ID="banking-ui"
CLIENT_SECRET="banking-ui-secret"
DEMO_USER="demo.user"
DEMO_EMAIL="demo.user@bank.test"
DEMO_PASSWORD="Demo@123"
REDIRECT_URI="http://localhost:8000/*"

echo "Waiting for Keycloak to be ready..."
until curl -sf "$KC_URL/realms/master" > /dev/null; do
  sleep 2
done
echo "Keycloak is up."

ADMIN_TOKEN=$(curl -sf -X POST "$KC_URL/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=admin-cli" -d "username=admin" -d "password=admin" -d "grant_type=password" \
  | jq -r .access_token)

auth_header=(-H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json")

if curl -sf "${auth_header[@]}" "$KC_URL/admin/realms/$REALM" > /dev/null 2>&1; then
  echo "Realm '$REALM' already exists, skipping creation."
else
  echo "Creating realm '$REALM'..."
  curl -sf -X POST "$KC_URL/admin/realms" "${auth_header[@]}" \
    -d "{\"realm\": \"$REALM\", \"enabled\": true}"
fi

CLIENT_UUID=$(curl -sf "${auth_header[@]}" "$KC_URL/admin/realms/$REALM/clients?clientId=$CLIENT_ID" | jq -r '.[0].id // empty')
if [ -n "$CLIENT_UUID" ]; then
  echo "Client '$CLIENT_ID' already exists, skipping creation."
else
  echo "Creating client '$CLIENT_ID'..."
  curl -sf -X POST "$KC_URL/admin/realms/$REALM/clients" "${auth_header[@]}" -d @- <<EOF
{
  "clientId": "$CLIENT_ID",
  "protocol": "openid-connect",
  "publicClient": false,
  "secret": "$CLIENT_SECRET",
  "standardFlowEnabled": true,
  "directAccessGrantsEnabled": true,
  "redirectUris": ["$REDIRECT_URI"],
  "webOrigins": ["*"],
  "enabled": true
}
EOF
fi

USER_ID=$(curl -sf "${auth_header[@]}" "$KC_URL/admin/realms/$REALM/users?username=$DEMO_USER" | jq -r '.[0].id // empty')
if [ -n "$USER_ID" ]; then
  echo "User '$DEMO_USER' already exists, skipping creation."
else
  echo "Creating demo user '$DEMO_USER'..."
  curl -sf -X POST "$KC_URL/admin/realms/$REALM/users" "${auth_header[@]}" -d @- <<EOF
{
  "username": "$DEMO_USER",
  "email": "$DEMO_EMAIL",
  "firstName": "Demo",
  "lastName": "User",
  "enabled": true,
  "emailVerified": true,
  "credentials": [{"type": "password", "value": "$DEMO_PASSWORD", "temporary": false}]
}
EOF
fi

echo ""
echo "Done. Demo login: $DEMO_USER / $DEMO_PASSWORD"
echo "Keycloak admin console: $KC_URL/admin (admin / admin)"
