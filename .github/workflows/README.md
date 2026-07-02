# CI Workflows (sourced from .github/workflows/)

Continuous integration and deployment for the Opita Code corporate landing (www.opitacode.com).

## Workflows

| File | Trigger | Purpose |
|---|---|---|
| `deploy.yml` | push to main, PR, manual | Build + typecheck + deploy to Cloudflare Pages + smoke test |

## Required secrets (set in GitHub repo settings)

| Secret | Source | Scope |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | Cloudflare dashboard → My Profile → API Tokens → Create Custom Token with **Cloudflare Pages: Edit** on `opita-code` project | Deploy only |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare dashboard → Workers & Pages → `opita-code` → right column | Identify account |

## Connection: GitHub → Cloudflare Pages

For the workflow to deploy automatically:
1. Cloudflare dashboard → Workers & Pages → `opita-code` → Settings → Builds
2. Disconnect the "no GitHub" state and connect this repo's `main` branch
3. Or keep GitHub Actions as the only source of truth (current setup)

The `pages-action` v1 deploys from the GitHub Actions runner; the Cloudflare git integration is a no-op fallback.

## Branch → environment mapping

| Branch | Cloudflare | URL |
|---|---|---|
| `main` | Production | https://www.opitacode.com |
| `*` (any other) | Preview | https://`<branch>`.opita-code.pages.dev |

## Local deploy (operator fallback)

If GitHub is unavailable, deploy from local:

```bash
# One-time: get a Cloudflare API token with Pages:Edit on opita-code
export CLOUDFLARE_API_TOKEN=...
export CLOUDFLARE_ACCOUNT_ID=...

# Build + deploy
npm ci
npm run build
npx wrangler pages deploy dist --project-name=opita-code --branch=main --commit-dirty=true
```

## Smoke test

After every deploy, the workflow curls `https://www.opitacode.com/es/` and fails the job if the response is not 200. This catches:
- Cloudflare propagation delays (10s wait)
- Build succeeded but routing broken
- DNS issue after Cloudflare zone changes
