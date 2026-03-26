# baptisteravina.com

Personal academic website built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install mkdocs-material mkdocs-macros-plugin
mkdocs serve
# Opens at http://127.0.0.1:8000
```

## Project structure

```
.
├── mkdocs.yml                  # Site config
├── main.py                     # Jinja macros (renders YAML → HTML)
├── data/
│   ├── publications.yml        # ← edit to add papers
│   └── talks.yml               # ← edit to add talks
├── overrides/
│   └── home.html               # Custom landing page template
├── docs/
│   ├── index.md                # Landing page (uses home.html)
│   ├── research.md             # Research themes
│   ├── publications.md         # Rendered from data/publications.yml
│   ├── talks.md                # Rendered from data/talks.yml
│   ├── team.md                 # Collaborators + alumni
│   ├── teaching.md             # Courses, seminars, BSc projects
│   ├── outreach.md             # Public talks, masterclasses, media
│   ├── assets/
│   │   ├── css/custom.css      # Site-wide styling
│   │   └── js/mathjax.js       # LaTeX config ($...$ notation)
│   └── blog/
│       ├── index.md            # Blog index
│       └── posts/              # ← drop blog posts here
└── site/                       # Built output (gitignored)
```

## Adding content

### New publication (~30 seconds)

Edit `data/publications.yml` — add at the top:

```yaml
- title: "My new measurement of X"
  authors: "ATLAS Collaboration (B. Ravina)"
  venue: "JHEP"
  date: 2026-03
  arxiv: "2603.12345"
  doi: "10.1007/JHEP03(2026)001"
  featured: true  # shows in Featured section
```

Optional fields: `hepdata`, `atlas_url`, `briefing`, `courier`, `type: thesis`.

BibTeX export buttons are generated automatically from the `arxiv` field via the INSPIRE-HEP API.

### New talk (~30 seconds)

Edit `data/talks.yml` — add at the top:

```yaml
- title: "My new talk"
  date: 2026-04-15
  venue: "Top Workshop"
  location: "CERN"
  indico: "https://indico.cern.ch/event/..."
  slides_url: "https://talks.baptisteravina.com/..."
  recording_url: "https://cds.cern.ch/record/..."
```

Only `title`, `date`, and `venue` are required. Links render as pill buttons on the talk card when present.

### New blog post

Create `docs/blog/posts/YYYY-slug.md`:

```yaml
---
date: 2026-03-25
categories:
  - ATLAS
  - Quantum information
---

# Title of my post

![Hero image](https://example.com/image.png){ .blog-hero }

Summary paragraph — shown in the blog index.

<!-- more -->

Full content below the fold.
```

**Categories** (pick from): `ATLAS`, `Machine learning`, `Top physics`, `Quantum information`. These are enforced in `mkdocs.yml` — a typo will fail the build. Categories appear as pills on each post and as navigation links in the blog sidebar.

**Hero images**: Use `{ .blog-hero }` after the image to make it span the full width. Optional but recommended for visual impact.

### New team member

Edit `docs/team.md`. Current collaborators get a profile card:

```html
<div class="team-card">
<div class="team-initials">XX</div>  <!-- or <img class="team-avatar" src="assets/team/photo.jpg"> -->
<div class="team-name">Name</div>
<div class="team-role">Role</div>
<div class="team-affiliation">University</div>
</div>
```

Alumni go into the Markdown table — one row per person.

### Teaching and outreach

Edit `docs/teaching.md` and `docs/outreach.md` directly. These are standard Markdown pages with no special templating.

## LaTeX support

Use `$...$` for inline math and `$$...$$` for display math. Works everywhere including publication titles in `data/publications.yml`. The `\(...\)` notation also works.

The mathjax config (`docs/assets/js/mathjax.js`) handles instant loading — LaTeX renders on first page load without needing a refresh.

## Build and deploy

```bash
# Build static site
mkdocs build
# Output: site/

# Deploy to GitHub Pages
mkdocs gh-deploy

# Or deploy to any static host (Netlify, CERN, etc.)
# Build command: mkdocs build
# Publish directory: site
```

## Customisation

**Profile photo**: Replace the `hp-avatar-placeholder` div in `overrides/home.html` with `<img class="hp-avatar" src="assets/team/baptiste.jpg">` and place the image in `docs/assets/team/`.

**Team photos**: Same approach — replace `<div class="team-initials">XX</div>` with `<img class="team-avatar" src="assets/team/name.jpg">` in `docs/team.md`.

**Landing page**: Edit `overrides/home.html`. This is a Jinja template extending `main.html` — it keeps the navigation header but replaces the content area. The career timeline, featured result, research cards, and blog preview are all plain HTML.

**Colours**: CSS variables in `docs/assets/css/custom.css` — search for `--accent` and `--teal-*`.

**Featured result**: Hardcoded in `overrides/home.html`. Update when you have a new highlight paper.

**Blog preview on landing page**: Also in `overrides/home.html`. Update the latest post manually, or automate with a build hook in `main.py`.
