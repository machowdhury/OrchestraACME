# Author-only documentation (not in this repository)

Campaign and blog materials live **only on your machine** under `docs/private/`. This folder is in `.gitignore` and is never pushed to GitHub.

## Setup (one time)

```bash
mkdir -p docs/private
```

## Private files (maintain locally)

| File | Purpose |
|------|---------|
| `docs/private/BLOG_USAGE_GUIDE.md` | 10-week campaign workflow, blog Splunk demos |
| `docs/private/BLOG_WRITER_PROMPTS.md` | Claude prompts for Track 1 + Track 2 posts |
| `docs/private/EMERGING_THREATS.md` | Threat classes mapped to campaign weeks (blog spine) |

If you cloned before the split, copy content from git history or recreate from your backup:

```bash
# Optional: recover old public USAGE_GUIDE from history
git show HEAD~1:docs/USAGE_GUIDE.md > docs/private/BLOG_USAGE_GUIDE.md
```

## Public documentation (published on GitHub)

| File | Audience |
|------|----------|
| [docs/USER_GUIDE.md](../USER_GUIDE.md) | All users — exploits, hunts, Splunk dashboards |
| [docs/THREAT_SURFACES.md](../THREAT_SURFACES.md) | Threat surface reference (no campaign/blog mapping) |
| [docs/CISCO_INTEGRATION.md](../CISCO_INTEGRATION.md) | Cisco AI Defense + MLTK overlay |
| [docs/BLOG_LAB_ALIGNMENT.md](../BLOG_LAB_ALIGNMENT.md) | 10-week blog ↔ lab mapping (public) |
| [README.md](../README.md) | Architecture and install |
