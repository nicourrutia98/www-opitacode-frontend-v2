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

`CLOUDFLARE_ACCOUNT_ID` is **not required** — wrangler resolves the account from the project name. (If you want to make it explicit anyway, add it from Cloudflare dashboard → Workers & Pages → `opita-code` → right column.)

## Connection: GitHub → Cloudflare Pages

The `cloudflare/wrangler-action@v3` step runs `wrangler pages deploy` from the GitHub Actions runner. **Do not** also connect the Cloudflare git integration — that would cause double-deploys. Pick one:
- ✅ **GitHub Action (this workflow)**: full CI, typecheck, smoke test, PR previews via `workflow_dispatch`
- ❌ Cloudflare's "Connect to Git" button: simpler but no typecheck, no smoke test, no PR previews

We use GitHub Action for the CI feedback loop.

## Branch → environment mapping

| Branch | Cloudflare | URL |
|---|---|---|
| `main` | Production | https://www.opitacode.com |
| `*` (PR or other branch) | Preview | https://`<branch>`.opita-code.pages.dev |

## Local deploy (operator fallback)

If GitHub is unavailable, deploy from local:

```bash
# Use the secret-vault token (no manual paste)
$CF_TOKEN = vault.ps1 get cloudflare_api_token
$env:CLOUDFLARE_API_TOKEN = $CF_TOKEN
npm ci
npm run build
npx wrangler pages deploy dist --project-name=opita-code --branch=main --commit-dirty=true
```

## Smoke test

After every deploy, the workflow curls `https://www.opitacode.com/es/` and fails the job if the response is not 200. This catches:
- Cloudflare propagation delays (10s wait)
- Build succeeded but routing broken
- DNS issue after Cloudflare zone changes
