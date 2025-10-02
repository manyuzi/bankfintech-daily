
# BankFintech Daily Digest (Public Page)

This repo generates a **public webpage** every day with your digest (title, summary, tags, link, structure).
It uses **GitHub Pages** (serving from the `docs/` folder) and **GitHub Actions** to rebuild daily.

## Quick Start (5–8 minutes)

1. Create a new **public** GitHub repo, e.g. `bankfintech-daily`.
2. Download this zip, unzip, and push/upload all files to your repo.
3. Settings → Pages → Build & deployment:
   - Source: **Deploy from a branch**
   - Branch: **main** and folder: **/docs**
4. Open your site: `https://<YOUR_GITHUB_USERNAME>.github.io/bankfintech-daily/`.
5. Optional: Actions → **Daily Build** → **Run workflow** (manual run).

> Schedule: daily at **00:30 UTC** (08:30 Beijing). Edit `.github/workflows/daily.yml` to change.
