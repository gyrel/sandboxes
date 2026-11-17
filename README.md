# Rheic documentation site

This is the public English and Russian documentation for the Rheic Sandboxes alpha. It replaces the earlier topic pages with a concise, version-identified comparison to Docker `sbx` v0.50.1 and a current native runtime release guide. Internal research and planning remain in the product's `PLAN.md` and `docs/REVERSE-ENGINEERING.md`.

Run `./dev.sh check` to build both languages strictly. The public site is deployed from `main` by `.github/workflows/pages.yml` after CI passes. The page source is under `docs/en` and `docs/ru`; keep the language pairs aligned and every parity claim tied to its method.
