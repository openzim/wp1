# OAuth Endpoints

> 20 nodes

## Key Concepts

- **oauth.py** (19 connections) — `wp1/web/oauth.py`
- **initiate()** (10 connections) — `wp1/web/oauth.py`
- **complete()** (8 connections) — `wp1/web/oauth.py`
- **users.py** (5 connections) — `wp1/logic/users.py`
- **route** (5 connections)
- **redirect_after_login()** (4 connections) — `wp1/web/oauth.py`
- **create_or_update_user()** (3 connections) — `wp1/logic/users.py`
- **User** (3 connections) — `wp1/models/wp10/user.py`
- **get_handshaker()** (3 connections) — `wp1/web/oauth.py`
- **create_user_session()** (3 connections) — `wp1/web/oauth.py`
- **identify()** (3 connections) — `wp1/web/oauth.py`
- **email()** (3 connections) — `wp1/web/oauth.py`
- **user_exists()** (2 connections) — `wp1/logic/users.py`
- **user.py** (2 connections) — `wp1/models/wp10/user.py`
- **get_homepage_url()** (2 connections) — `wp1/web/oauth.py`
- **has_oauth_credentials()** (2 connections) — `wp1/web/oauth.py`
- **create_fake_dev_user()** (2 connections) — `wp1/web/oauth.py`
- **logout()** (2 connections) — `wp1/web/oauth.py`
- **Logic for user creation and management.** (1 connections) — `wp1/logic/users.py`
- **s** (1 connections)

## Relationships

- [Builders Web Endpoints](Builders_Web_Endpoints.md) (4 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (2 shared connections)
- [ZIM Email Endpoints](ZIM_Email_Endpoints.md) (2 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)

## Source Files

- `wp1/logic/users.py`
- `wp1/models/wp10/user.py`
- `wp1/web/oauth.py`

## Audit Trail

- EXTRACTED: 83 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
