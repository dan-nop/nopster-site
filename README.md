# nopster-site

Company site for Nopster, Inc. — static HTML, no build step, no dependencies.

## Local preview

Just open `index.html` in a browser, or run a quick local server:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Push to GitHub

From inside this folder:

```bash
git init
git add .
git commit -m "Initial site"
git branch -M main
git remote add origin https://github.com/dan-nop/nopster-site.git
git push -u origin main
```

If the repo doesn't exist yet on GitHub, create it first:
1. Go to https://github.com/new
2. Repository name: `nopster-site`
3. Keep it **Public** (Cloudflare Pages free tier needs to read it) or Private if you have Cloudflare Pro — Public is simplest
4. Don't initialize with a README (you already have one) — leave all the init checkboxes unchecked
5. Create repository, then run the commands above

## Connect to Cloudflare Pages

1. Log into Cloudflare → **Workers & Pages** (left sidebar) → **Create application** → **Pages** tab → **Connect to Git**
2. Authorize Cloudflare to access your GitHub account, select the `nopster-site` repo
3. Build settings:
   - **Framework preset:** None
   - **Build command:** (leave blank)
   - **Build output directory:** `/` (root — since it's a static file, not a build output)
4. Deploy — Cloudflare will give you a `*.pages.dev` URL immediately

## Point nopster.dev at it

1. In the Cloudflare Pages project, go to **Custom domains** → **Set up a custom domain**
2. Enter `nopster.dev` (and optionally `www.nopster.dev`)
3. Since the domain is already in the same Cloudflare account, DNS records are added automatically — no manual copying needed

## Updating the site later

Any time you want to change something:

```bash
# edit index.html
git add .
git commit -m "Describe what changed"
git push
```

Cloudflare Pages auto-deploys on every push to `main` — usually live within a minute. That's your version history and your deploy pipeline in one.

## Updating the capability statement PDF

Once SAM.gov validation completes and you have your real UEI/CAGE code, regenerate the PDF with the real values, replace `capability-statement.pdf` in this folder, commit, and push — same flow as above.
