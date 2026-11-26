# Gyrel documentation site

<img src="docs/assets/gyrel-shark.png" alt="Gyrel shark logo" width="180">

This directory contains reader-facing documentation in English and Russian. Internal implementation notes remain in the parent `docs/` directory.

## Run and check locally

```sh
./docs/site/dev.sh
```

The script creates a local virtual environment and installs the pinned dependencies on first run, then serves a live preview at `http://127.0.0.1:8000`. If this Gyrel preview is already running on the selected port, it reports that address; if another process owns the port, it picks the next available port. Run `./docs/site/dev.sh check` to build both languages with strict warnings and verify their output pages. The check uses a temporary directory and leaves no generated site in the repository. Set `DOCS_HOST` or `DOCS_PORT` to choose the starting address.

The i18n plugin emits English at the site root and Russian under `/ru/`; keep the same page set in both locale directories.

## Visual direction

The documentation uses a compact persistent header with sticky topic navigation, prominent search, a guided landing page, and task-oriented topic cards. Gyrel keeps its own copy and supplied shark logo. The reading canvas uses neutral white, graphite text, blue-gray surfaces, and a DeepSeek-inspired blue accent with a restrained serif display face, sans-serif body text, fine borders, and softly rounded cards. The command preview uses macOS window controls with Dracula-colored code. Fonts are local system fallbacks; the site does not fetch fonts or images from third parties.

English and Russian pages keep matching paths and navigation. The home page exposes the quick start, search, developer journey, project status, topic directory, and common questions. Guide pages retain the documentation tree and table of contents. Test contextual language switching, search, mobile layout, keyboard focus, dark mode, and reduced-motion behavior. Keep project status factual and distinguish tested behavior from planned or blocked paths.
