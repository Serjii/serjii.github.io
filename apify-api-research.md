# Apify REST API v2 — Research Findings

**Date:** 2026-10-27  
**Source:** [Apify API Documentation](https://docs.apify.com/api/v2.md), [OpenAPI Schema (JSON)](https://docs.apify.com/api/openapi.json), live API testing

---

## 1. Is authentication required for `/v2/actors` endpoints?

### `GET /v2/actors` (list all actors) — ❌ **Always requires authentication**

The list endpoint **always requires a valid API token**, regardless of query parameters.

```bash
# Without token → 401
$ curl -s https://api.apify.com/v2/actors
{"error":{"type":"token-not-provided","message":"Authentication token was not provided"}}
```

```bash
# Even with an invalid token → 401
$ curl -s -H "Authorization: Bearer invalid_token" \
  "https://api.apify.com/v2/actors?my=1"
{"error":{"type":"user-or-token-not-found","message":"User was not not found or authentication token is not valid"}}
```

### `GET /v2/actors/{actorId}` (get single actor) — ✅ **No auth needed for PUBLIC actors**

For public actors, you can use the **`username~actor-name`** format without any API token.

```bash
# Without token — works for public actors! → 200 OK
$ curl -s "https://api.apify.com/v2/actors/apify~hello-world" | python3 -m json.tool | head -30
{
  "data": {
    "id": "E2jjCZBezvAZnX8Rb",
    "userId": "ZscMwFR5H7eCtWtyh",
    "name": "hello-world",
    "username": "apify",
    "description": "The simplest Actor you will see today...",
    "isPublic": true,
    ...
```

**But for private actors, authentication IS required:**
```bash
# Private actor without token → 401
$ curl -s "https://api.apify.com/v2/actors/private_user~secret-actor"
{"error":{"type":"token-not-provided","message":"Authentication token was not provided"}}
```

### `GET /v2/users/{userId}` (get user profile) — ✅ **No auth needed**

```bash
$ curl -s "https://api.apify.com/v2/users/ZscMwFR5H7eCtWtyh"
{
  "data": {
    "username": "apify",
    "profile": {
      "bio": "The official profile of Apify on Apify ⚡",
      "name": "Apify",
      "pictureUrl": "...",
      "githubUsername": "apify",
      "twitterUsername": "@apify"
    }
  }
}
```

---

## 2. What authentication options does the Apify API support?

The Apify API supports **two authentication methods** (defined in the OpenAPI schema):

### Method 1: Bearer Token (Recommended)

```
Authorization: Bearer <YOUR_API_TOKEN>
```

This is the **preferred** method. Headers are not logged in browser history or server logs.

### Method 2: Query Parameter Token (Less secure)

```
?token=<YOUR_API_TOKEN>
```

The docs explicitly warn: *"Add it as the token parameter to your request URL. (Less secure)."*

### Method 3: Agentic Payments (Experimental, 2026)

For AI agents without Apify accounts:
- **x402 protocol:** `PAYMENT-SIGNATURE` header
- **Skyfire:** `skyfire-pay-id` header

### There is NO Basic Auth support

The API does **not** support HTTP Basic Authentication (no `Authorization: Basic ...` header).

### Where to find your token

Go to [Apify Console → Integrations](https://console.apify.com/settings/integrations) → copy your secret API token.

---

## 3. Fields: List endpoint vs Detail endpoint

### 3.1 `GET /v2/actors?my=1` (List endpoint)

**Requires authentication.** Returns a paginated list with **minimal** fields per actor.

**Response structure:**
```json
{
  "data": {
    "total": 2,
    "count": 2,
    "offset": 0,
    "limit": 1000,
    "desc": false,
    "items": [
      {
        "id": "br9CKmk457",
        "createdAt": "2019-10-29T07:34:24.202Z",
        "modifiedAt": "2019-10-30T07:34:24.202Z",
        "name": "MyAct",
        "username": "janedoe",
        "title": "Hello World Example",
        "stats": {
          "totalBuilds": 9,
          "totalRuns": 16,
          "totalUsers": 6,
          "totalUsers7Days": 2,
          "totalUsers30Days": 6,
          "totalUsers90Days": 6,
          "totalMetamorphs": 2,
          "lastRunStartedAt": "2019-07-08T14:01:05.546Z",
          "actorReviewCount": 69,
          "actorReviewRating": 4.7,
          "bookmarkCount": 1269,
          "publicActorRunStats30Days": {
            "ABORTED": 2542,
            "FAILED": 1234,
            "SUCCEEDED": 732805,
            "TIMED-OUT": 12556,
            "TOTAL": 749137
          }
        }
      }
    ]
  }
}
```

**Fields in list response per item:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Actor ID |
| `createdAt` | datetime | Creation timestamp |
| `modifiedAt` | datetime | Last modification timestamp |
| `name` | string | Actor name (slug) |
| `username` | string | Owner username |
| `title` | string (nullable) | Human-readable title |
| `stats` | object or null | Aggregate statistics |
| `stats.totalBuilds` | integer | Total builds |
| `stats.totalRuns` | integer | Total runs |
| `stats.totalUsers` | integer | Total users including owner |
| `stats.totalUsers7Days` | integer | Active users (7d) |
| `stats.totalUsers30Days` | integer | Active users (30d) |
| `stats.totalUsers90Days` | integer | Active users (90d) |
| `stats.totalMetamorphs` | integer | Total metamorphs |
| `stats.lastRunStartedAt` | datetime | Last run start time |
| `stats.actorReviewCount` | integer | Number of reviews |
| `stats.actorReviewRating` | number | Average rating |
| `stats.bookmarkCount` | integer | Number of bookmarks |
| `stats.publicActorRunStats30Days` | object | 30-day run status breakdown (only for public actors) |
| `stats.publicActorRunStats30Days.ABORTED` | integer | Aborted runs (30d) |
| `stats.publicActorRunStats30Days.FAILED` | integer | Failed runs (30d) |
| `stats.publicActorRunStats30Days.SUCCEEDED` | integer | Succeeded runs (30d) |
| `stats.publicActorRunStats30Days.TIMED-OUT` | integer | Timed out runs (30d) |
| `stats.publicActorRunStats30Days.TOTAL` | integer | Total runs (30d) |

---

### 3.2 `GET /v2/actors/{actorId}` (Detail endpoint)

**No auth needed for public actors.** Returns **all** details about an actor.

**Full response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Actor ID |
| `userId` | string | Owner user ID |
| `name` | string | Actor name (slug) |
| `username` | string | Owner username |
| `description` | string / null | Short description |
| `restartOnError` | boolean / null | *(deprecated)* Auto-restart on error |
| `isPublic` | boolean | Whether public in Apify Store |
| `actorPermissionLevel` | string | `LIMITED_PERMISSIONS` or `FULL_PERMISSIONS` |
| `createdAt` | datetime | Creation timestamp |
| `modifiedAt` | datetime | Last modification timestamp |
| `stats` | object | *(same as list endpoint — see above)* |
| `versions` | array | Version history with source code |
| `versions[].versionNumber` | string | Semantic version (MAJOR.MINOR) |
| `versions[].sourceType` | string | `SOURCE_FILES`, `GIT_REPO`, `TARBALL`, `GITHUB_GIST`, `SOURCE_CODE` |
| `versions[].envVars` | array or null | Environment variables |
| `versions[].envVars[].name` | string | Variable name |
| `versions[].envVars[].value` | string | Variable value |
| `versions[].envVars[].isSecret` | boolean / null | Whether encrypted |
| `versions[].applyEnvVarsToBuild` | boolean / null | Inject at build time? |
| `versions[].buildTag` | string / null | Build tag (e.g. "latest") |
| `versions[].sourceFiles` | array | File contents (when sourceType=SOURCE_FILES) |
| `versions[].gitRepoUrl` | string / null | Git repo URL |
| `versions[].tarballUrl` | string / null | Tarball/ZIP URL |
| `versions[].gitHubGistUrl` | string / null | GitHub Gist URL |
| `pricingInfos` | array | Pricing records |
| `defaultRunOptions` | object | Default run configuration |
| `defaultRunOptions.build` | string | Build tag or version |
| `defaultRunOptions.timeoutSecs` | integer | Timeout in seconds |
| `defaultRunOptions.memoryMbytes` | integer | Memory in MB |
| `defaultRunOptions.restartOnError` | boolean | Auto-restart on error |
| `defaultRunOptions.maxItems` | integer / null | Max output items |
| `defaultRunOptions.maxTotalChargeUsd` | number / null | Max cost in USD |
| `exampleRunInput` | object | Sample input JSON |
| `exampleRunInput.body` | string | Serialized input |
| `exampleRunInput.contentType` | string | MIME type |
| `isDeprecated` | boolean / null | Is deprecated |
| `deploymentKey` | string | Public SSH key (detail only) |
| `title` | string / null | Human-readable title |
| `taggedBuilds` | object | Build tag → build info mapping |
| `actorStandby` | object / null | Standby mode configuration |
| `readmeSummary` | string | AI-generated README summary (public actors only) |
| `seoTitle` | string / null | SEO title |
| `seoDescription` | string / null | SEO description |
| `pictureUrl` | string / null | Icon image URL |
| `standbyUrl` | string / null | Standby endpoint URL |
| `notice` | string / null | Warning notice (`NONE`, `RESIDENTIAL_PROXY_REQUIRED`, etc.) |
| `categories` | array | Category tags |
| `isCritical` | boolean | Maintained by Apify |
| `isGeneric` | boolean | Intended for developers |
| `isSourceCodeHidden` | boolean | Source files hidden on detail page |
| `hasNoDataset` | boolean | Whether actor stores no dataset |

---

### 3.3 Summary comparison

| Feature | List (`GET /v2/actors`) | Detail (`GET /v2/actors/{id}`) |
|---------|------------------------|-------------------------------|
| Auth required | **Always** | Only for private actors |
| Pagination | Yes (offset/limit/desc) | No |
| `versions` array | ❌ Not included | ✅ Full version history |
| `pricingInfos` | ❌ Not included | ✅ Full pricing records |
| `defaultRunOptions` | ❌ Not included | ✅ Run config |
| `exampleRunInput` | ❌ Not included | ✅ Sample input |
| `deploymentKey` | ❌ Not included | ✅ SSH key |
| `readmeSummary` | ❌ Not included | ✅ AI summary |
| `seoTitle`/`seoDescription` | ❌ Not included | ✅ SEO fields |
| `pictureUrl` | ❌ Not included | ✅ Image URL |
| `notice` | ❌ Not included | ✅ Warning notice |
| `categories` | ❌ Not included | ✅ Category tags |
| `isSourceCodeHidden` | ❌ Not included | ✅ Source code visibility |
| `taggedBuilds` | ❌ Not included | ✅ Build tag mapping |
| `actorStandby` | ❌ Not included | ✅ Standby config |

---

## 4. Rate limits for unauthenticated requests

### Global rate limit

| Type | Limit | Counting |
|------|-------|----------|
| **Authenticated** | 250,000 requests/minute | Per user |
| **Unauthenticated** | 250,000 requests/minute | Per IP address |

### Per-resource rate limit

- **Default:** 60 requests/second per resource (e.g. per actor)
- Returned in response header: `X-RateLimit-Limit: 60`

### Rate limit headers

Every response includes:
- `X-Apify-Pagination-Total` — Total items available
- `X-Apify-Pagination-Offset` — Current offset
- `X-Apify-Pagination-Limit` — Max items per page
- `X-Apify-Pagination-Count` — Items in current response
- `X-Apify-Pagination-Desc` — Sort direction
- `X-RateLimit-Limit` — Rate limit for the endpoint

### Rate limit exceeded response

```json
{
  "error": {
    "type": "rate-limit-exceeded",
    "message": "You have exceeded the rate limit of 60 requests per second"
  }
}
```

Response code: **429 Too Many Requests**

### Recommended retry strategy (exponential backoff)

1. Start with `DELAY = 500ms`
2. On 429: wait random(DELAY, 2*DELAY) ms, double DELAY, retry

---

## 5. Is the `my=1` filter available without authentication?

### ❌ **No — `my=1` always requires authentication**

The `my=1` parameter filters to "Actors owned by the current user." Since the API has no concept of "current user" without authentication, this parameter is **inaccessible without a valid API token**.

```bash
# Without token
$ curl -s "https://api.apify.com/v2/actors?my=1"
{"error":{"type":"token-not-provided","message":"Authentication token was not provided"}}

# With valid token
$ curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.apify.com/v2/actors?my=1&limit=2"
{
  "data": {
    "total": 11,
    "count": 2,
    "offset": 0,
    "limit": 2,
    "desc": false,
    "items": [
      {
        "id": "...",
        "name": "...",
        "username": "serj_henrique",
        ...
      }
    ]
  }
}
```

The error message is specifically `"Authentication token was not provided"` (not `"User was not found"`), confirming the request never reaches the auth check — it's rejected at the token validation stage.

---

## 6. Workarounds for public actor data without authentication

Since the list endpoint always requires auth, but the detail endpoint works for public actors without auth, here are the alternatives:

### Option A: Scrape the public profile page

The Apify Store profile page at `https://apify.com/serj_henrique` displays:
- Actor name, description, and URL
- Actor stats (runs, users, etc.)
- 11 public actors listed

This data can be fetched without any API token.

### Option B: Use the detail endpoint with known actor names

If you know the actor name, you can call the detail endpoint directly:

```bash
# Works without auth for public actors
curl -s "https://api.apify.com/v2/actors/serj_henrique~actor-name"
```

### Option C: Use the user public data endpoint

Get the user's public profile info without auth:

```bash
curl -s "https://api.apify.com/v2/users/<USER_ID>"
```

### Option D: Find actor IDs from the Apify Store

The Apify Store pages for each actor include the actor ID in the URL, which can then be used with the detail endpoint.

---

## 7. Live test results summary

| Endpoint | Auth | Status | Notes |
|----------|------|--------|-------|
| `GET /v2/actors` | None | 401 | `"token-not-provided"` |
| `GET /v2/actors?my=1` | None | 401 | `"token-not-provided"` |
| `GET /v2/actors?my=1` | Invalid token | 401 | `"user-or-token-not-found"` |
| `GET /v2/actors/apify~hello-world` | None | **200** | Public actor — full data |
| `GET /v2/users/<USER_ID>` | None | **200** | Public user profile |

---

## 8. Key takeaways

1. **`GET /v2/actors` (list) always requires an API token** — there is no unauthenticated way to list all actors.
2. **`GET /v2/actors/{actorId}` works without auth for public actors** — use `username~actor-name` format.
3. **`my=1` is gated behind authentication** — it filters by the authenticated user's own actors.
4. **Two auth methods:** `Authorization: Bearer <token>` (recommended) or `?token=<token>` (less secure). No Basic Auth.
5. **Rate limits:** 250K req/min global (per IP if unauthenticated), 60 req/sec per resource default.
6. **Public user profile** (`GET /v2/users/{userId}`) is freely accessible without auth.
7. **For full actor data without auth**, the detail endpoint returns significantly more fields than the list endpoint, including source code, pricing, versions, SEO metadata, and more.
