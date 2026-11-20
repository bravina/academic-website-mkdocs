# baptisteravina.com

Personal academic website, built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). Most content lives in YAML files under `data/` and is turned into HTML by Jinja macros in `main.py`, so routine updates (a paper, a talk, a student) mean editing one YAML file.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # pinned versions
mkdocs serve                      # http://127.0.0.1:8000
```

## Deployment

Every push to `main` builds and publishes the site through GitHub Pages ([.github/workflows/deploy.yml](.github/workflows/deploy.yml)). The workflow also writes the `CNAME` file for `baptisteravina.com`.

## Project structure

```
.
├── mkdocs.yml               # Site configuration, navigation, blog category colours
├── main.py                  # Jinja macros: YAML → HTML for every data-driven section
├── hooks.py                 # "Last updated" date of a page follows its data file
├── requirements.txt         # Pinned Python dependencies
├── data/
│   ├── profile.yml          # Homepage hero: name, role, affiliations, bio, tags, email
│   ├── research.yml         # Research topics: front-page cards, research-page icons
│   ├── career.yml           # Homepage career timeline
│   ├── publications.yml     # Publications page and homepage "Featured results"
│   ├── talks.yml            # Talks page
│   ├── team.yml             # Team page: students, collaborators, alumni
│   └── card-anims/          # One animation per research topic (SVG, named after its key)
├── docs/
│   ├── index.md             # Homepage (layout from overrides/home.html)
│   ├── research.md          # Research page: text written by hand, plus macros
│   ├── publications.md      # publications_page() + the BibTeX pop-up
│   ├── talks.md             # talks_page()
│   ├── team.md              # team_students(), team_collaborators(), team_alumni()
│   └── assets/
│       ├── css/custom.css   # All site styling (colours are CSS variables at the top)
│       ├── js/home.js       # Homepage: event display, timeline, card animations
│       ├── js/pages.js      # Filter chips, publication timeline, copy-BibTeX button
│       ├── js/mathjax.js    # LaTeX configuration
│       ├── figures/         # Research-page figures
│       ├── team/            # Portraits
│       ├── logos/           # Career timeline logos
│       └── uploads/         # Slides hosted on the site
├── overrides/               # Theme templates (homepage, blog post and post list)
└── drafts/                  # Not built: teaching and outreach pages, blog posts
```

## Adding content

### Publication

Add an entry to `data/publications.yml`:

```yaml
- title: "My new measurement of $t\\bar{t}Z$"
  authors: "ATLAS Collaboration"
  venue: "JHEP"
  date: 2026-03
  arxiv: "2603.12345"
  doi: "10.1007/JHEP03(2026)001"
  type: [top, quantum]   # topic tags and filters, see PUB_TYPES in main.py
  featured: true         # star in the list, ringed dot in the timeline, homepage
```

Optional links: `hepdata`, `atlas_url`, `briefing`, `courier`, `rivet`, `git`, and `inspirehep` (an INSPIRE record ID, used when there is no arXiv number). The BibTeX button fetches the entry from INSPIRE-HEP when clicked.

### Talk

Add an entry to `data/talks.yml`:

```yaml
- title: "My new talk"
  date: 2026-04-15
  venue: "ATLAS Top Workshop"
  type: atlas              # seminar | conference | workshop | atlas
  location: "CERN"
  indico: "https://indico.cern.ch/event/.../contributions/.../"
  slides_url: "https://indico.cern.ch/.../slides.pdf"
  recording_url: "https://..."
```

Only `title`, `date` and `venue` are required. `type` sets the coloured tag and the filter chip. Slides stored on the site go in `docs/assets/uploads/` and are linked as `/assets/uploads/file.pdf`.

### Team member

Edit `data/team.yml`:

- **Current students** go under `students:` and **collaborators** under `collaborators:`, with `name`, `role` and `affiliation`. For a photo, add the file to `docs/assets/team/` and set `photo:`; without one, the card shows initials.
- **Alumni** go under `alumni:` with `role_type` (BSc, MSc, PhD, ...), `project`, `location`, `year` and, if known, `next_position`. Someone with several projects gets an `entries:` list instead, one item per project. Each role type automatically gets a filter chip.

### Research

- **Text:** edit `docs/research.md` directly. Each topic heading carries its icon and a fixed anchor, for example `## {{ research_icon('top') }} Top quark and electroweak physics {: #top-quark-and-electroweak-physics }`. Keep the anchor in sync with the topic's `link` in `research.yml`.
- **Topics:** each entry in `data/research.yml` has a `key` (used by the macros), the publication `type` it counts (`pubs`), an icon (`logo`), a colour and the front-page card text.
- **Figures:** put the image in `docs/assets/figures/` and use the `<figure class="plot">` blocks already in `research.md` as a template. Wrap two figures in `<div class="plot-pair">` to show them side by side.

### Career

Edit `data/career.yml`; entries appear in the order written. Logos go in `docs/assets/logos/`.

## Blog (currently off)

The blog posts live in `drafts/blog/`. To turn the blog on:

1. Move `drafts/blog/` to `docs/blog/`.
2. Uncomment the `blog` plugin and the `Blog` navigation entry in `mkdocs.yml`.

The homepage then shows the latest post. Category pills take their colour from `extra.blog_category_colors` in `mkdocs.yml`; the allowed categories are listed under the plugin's `categories_allowed`.

## LaTeX

Use `$...$` inline and `$$...$$` for display maths, in Markdown pages and in YAML titles alike. In YAML strings, backslashes must be doubled: `"$t\\bar{t}Z$"`. Add `class="nomath"` to an element to keep MathJax away from it.
