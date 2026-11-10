# SLFN Business OS — OIDC Flow Test Walkthrough

## Prerequisites (Already Done)
- ✅ Authentik running at `http://localhost:9000`
- ✅ OIDC Provider "SLFN Business OS" created with:
  - Client ID: `6S8KcTVwB0euO1owAmU1y1XRLcTVoJCLkGdhCa9b`
  - Client Secret: (configured in backend)
  - Realm: `slfn-business-os`
  - Redirect URIs: `http://localhost:3002/login`, `http://localhost:8081/api/v1/auth/authentik/callback`
  - Scopes: `openid`, `email`, `profile`
- ✅ Backend config updated with client credentials
- ✅ Auth flows assigned (authentication, authorization, invalidation)
- ✅ All 6 services healthy

---

## Test Steps

### 1. Open Frontend Login Page
```
http://localhost:3002/login
```
You should see:
- "Login" heading
- **Blue button**: "Continue with Authentik SSO" (with Authentik logo)
- Divider: "Or continue with email"
- Email/password form (local auth fallback)

### 2. Click "Continue with Authentik SSO"
This redirects to:
```
http://localhost:9000/application/o/authorize/
  ?client_id=6S8KcTVwB0euO1owAmU1y1XRLcTVoJCLkGdhCa9b
  &redirect_uri=http%3A%2F%2Flocalhost%3A3002%2Flogin
  &response_type=code
  &scope=openid%20email%20profile
  &state=<random>
```

You should see the **Authentik login page** (not "Not Found"):
- Email field
- Password field
- "Sign in" button
- "Forgot password?" link (if configured)

### 3. Login with Admin Credentials
```
Email: admin@slfn.local
Password: slfn-admin-pass
```

### 4. Consent Screen (if prompted)
Since this is a first-party app with implicit consent flow, you may see:
- "Authorize Application" screen
- Scopes requested: openid, email, profile
- Click "Authorize" / "Allow"

### 5. Redirect Back to Frontend
After successful auth, Authentik redirects to:
```
http://localhost:3002/login?code=<auth_code>&state=<state>
```

The frontend Login page:
1. Receives the `code` and `state` from URL params
2. Exchanges code for tokens via backend `/api/v1/auth/authentik/callback`
3. Stores `access_token` (local JWT) + `authentik_token` in localStorage
4. Redirects to `/dashboard`

### 6. Verify Dashboard Access
You should land on `/dashboard` with:
- User info displayed (from `/api/v1/auth/me`)
- Navigation sidebar: Dashboard, Contacts, Deals, Forms, Settings
- Authenticated state persists on refresh

---

## Expected Token Flow

```
┌─────────────┐     1. Click SSO      ┌──────────────┐
│   Browser   │ ────────────────────► │  Frontend    │
│  (User)     │                       │  (3002)      │
└─────────────┘                       └──────┬───────┘
                                             │
                                             │ 2. Redirect to Authentik
                                             ▼
┌─────────────┐                       ┌──────────────┐
│   Browser   │ ◄──────────────────── │  Authentik   │
│  (User)     │   3. Login Page       │  (9000)      │
└─────────────┘                       └──────┬───────┘
                                             │
                                             │ 4. Submit credentials
                                             ▼
┌─────────────┐                       ┌──────────────┐
│   Browser   │ ◄──────────────────── │  Authentik   │
│  (User)     │   5. Consent (opt)   │  (9000)      │
└─────────────┘                       └──────┬───────┘
                                             │
                                             │ 6. Redirect with code
                                             ▼
┌─────────────┐     7. GET /login         ┌──────────────┐
│   Browser   │ ────────────────────────► │  Frontend    │
│  (User)     │   ?code=xxx&state=yyy     │  (3002)      │
└─────────────┘                           └──────┬───────┘
                                                 │
                                                 │ 8. POST /api/v1/auth/authentik/callback
                                                 ▼
┌─────────────┐                       ┌──────────────┐
│   Browser   │ ◄──────────────────── │   Backend    │
│  (User)     │   9. Tokens + redirect│  (8081)      │
└─────────────┘                       └──────┬───────┘
                                                 │
                                                 │ 10. Validate JWT with Authentik JWKS
                                                 ▼
┌─────────────┐                       ┌──────────────┐
│   Browser   │ ◄──────────────────── │  Authentik   │
│  (User)     │   11. JWKS / Userinfo │  (9000)      │
└─────────────┘                       └──────────────┘
```

---

## Verification Checklist

| Step | Expected Result |
|------|-----------------|
| 1. Open login page | Shows "Continue with Authentik SSO" button |
| 2. Click SSO button | Redirects to Authentik login (not 404) |
| 3. Login with admin@slfn.local | Success, no errors |
| 4. Consent screen | Shows "SLFN Business OS" requesting openid, email, profile |
| 5. Redirect to frontend | URL contains `?code=...&state=...` |
| 6. Dashboard loads | Shows authenticated UI, user info |
| 7. Refresh page | Stays logged in (localStorage token) |
| 8. Logout | Clears tokens, returns to login |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Not Found" on authorize | Flows not assigned → run flow assignment script |
| "Invalid redirect_uri" | Check exact match in provider redirect_uris |
| "Invalid client" | Verify Client ID/Secret in backend config |
| CORS error | Check `ALLOWED_ORIGINS` includes `http://localhost:3002` |
| Token validation fails | Check JWKS endpoint accessible, realm matches |
| Infinite redirect loop | Check frontend handles callback correctly |

---

## Key Endpoints for Debugging

| Endpoint | Purpose |
|----------|---------|
| `http://localhost:9000/application/o/slfn-business-os/.well-known/openid-configuration` | OIDC discovery |
| `http://localhost:9000/application/o/slfn-business-os/jwks/` | Public keys for JWT validation |
| `http://localhost:8081/api/v1/auth/authentik/login` | Frontend → backend redirect to Authentik |
| `http://localhost:8081/api/v1/auth/authentik/callback` | Code exchange → tokens |
| `http://localhost:8081/api/v1/auth/me` | Get current user (requires valid JWT) |

---

## Next After Successful Test
1. Seed Guidance Engine with business phases/checklists
2. Build frontend Guidance UI pages
3. Build Document Intake UI
4. Configure MFA for admin users in Authentik