# API security

## Allowed frontend origins

`CLIENT_DOMAINS` is the shared allowlist for credentialed CORS and session
mutation protection. Configure a non-empty comma-separated list of **exact
HTTP(S) origins**, such as `https://wp1.openzim.org,http://localhost:5173`.
Include the scheme and any non-default port, but no trailing slash, path,
query, fragment, or user information. Wildcards, regular-expression patterns,
`null`, and empty lists (including separator-only input) are rejected at
startup. Production must explicitly provide this setting; development defaults
to `http://localhost:5173`. Trust only frontends you control, not all sibling
subdomains.

## Credentialed requests and CSRF protection

Every unsafe request (`POST`, `PUT`, `PATCH`, `DELETE`, etc.) to a
session-authenticated endpoint must include an `Origin` that exactly matches
this allowlist. If `Origin` is absent, the server accepts a valid HTTP(S)
`Referer` whose origin exactly matches instead. An empty, `null`, malformed,
or untrusted `Origin` is rejected even when `Referer` is trusted; requests
missing both headers are also rejected with HTTP 403. This check prevents
mutations independently of whether the browser can read a CORS response.

Browsers send `Origin` automatically for frontend mutations. Cookie-authenticated
scripts must now explicitly send a configured origin, for example
`Origin: http://localhost:5173`, along with their session cookie. CORS does not
grant authentication: a valid session is still required. OAuth login/callback
GET requests and token-authenticated Zimfarm webhooks and email links do not
require these headers.

## Logout

Logout is **`POST /v1/oauth/logout`**, with credentials and the same origin
requirements. `GET /v1/oauth/logout` returns HTTP 405 and never logs the user
out. An unauthenticated logout returns HTTP 401.

## ZIM notification privacy

ZIM build status remains public at `/v1/builders/{builderId}/zim/status`.
Active schedule details (including email and schedule ID) are returned only
to the authenticated builder owner; anonymous users and other users receive
`active_schedule: null`. Browser clients must include session credentials
to display the owner's schedule controls.

Notification emails use
`${CLIENT_API_URL}/v1/zim/unsubscribe-notification?token=...`, where
`CLIENT_API_URL` is the API base URL without the `/v1` suffix. The signed,
purpose-specific capability authorizes anonymous unsubscribe only for its
schedule and current recipient email. Keep these links private. Changing
the recipient or rotating `SESSION_SECRET_KEY` invalidates existing links.
Old `schedule_id`-only email links no longer authorize unsubscribe; recipients
need a newly generated notification link or can manage the schedule while
logged in. The separate email confirmation and decline links are unchanged.
