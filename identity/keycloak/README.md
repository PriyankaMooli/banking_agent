# Keycloak SSO (dev setup)

Runs a local Keycloak instance and provisions a realm, client, and demo user
for the banking assistant's login.

## 1. Start Keycloak

```
docker compose -f identity/keycloak/docker-compose.yml up -d
```

Admin console: http://localhost:8080/admin (admin / admin)

## 2. Provision the realm, client, and demo user

```
bash identity/keycloak/provision.sh
```

Creates:
- Realm: `banking`
- Client: `banking-ui` (confidential, secret `banking-ui-secret`, redirect `http://localhost:8000/*`)
- Demo user: `demo.user` / `Demo@123`

Safe to re-run — skips anything that already exists.

## 3. Configure the app

Copy `.env.example` to `.env` at the project root and fill in
`CHAINLIT_AUTH_SECRET` (generate with `chainlit create-secret`). The
`OAUTH_KEYCLOAK_*` values already match what `provision.sh` creates.

## 4. Run and log in

```
chainlit run ui/app.py
```

Chainlit shows a "Continue with Keycloak" button before the chat loads.
Log in as `demo.user` / `Demo@123` and you should land in the chat, greeted
by your Keycloak username.
