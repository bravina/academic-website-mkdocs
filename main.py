"""
MkDocs Macros plugin — loads all YAML data and provides rendering macros.
"""
import yaml
import os
from datetime import date


def define_env(env):
    data_dir = os.path.join(env.project_dir, "data")

    def _load(filename):
        path = os.path.join(data_dir, filename)
        with open(path) as f:
            return yaml.safe_load(f) or []

    pubs = _load("publications.yml")
    talks = _load("talks.yml")
    team = _load("team.yml")
    profile = _load("profile.yml")
    research = _load("research.yml")
    career = _load("career.yml")

    # ==================================================================
    # PUBLICATION HELPERS
    # ==================================================================

    def _pub_links(pub):
        links = []
        if pub.get("arxiv"):
            links.append(f'<a href="https://arxiv.org/abs/{pub["arxiv"]}">arXiv</a>')
        if pub.get("doi"):
            links.append(f'<a href="https://doi.org/{pub["doi"]}">DOI</a>')
        if pub.get("hepdata"):
            links.append(f'<a href="{pub["hepdata"]}">HEPData</a>')
        if pub.get("atlas_url"):
            links.append(f'<a href="{pub["atlas_url"]}">ATLAS</a>')
        if pub.get("briefing"):
            links.append(f'<a href="{pub["briefing"]}">Briefing</a>')
        if pub.get("courier"):
            links.append(f'<a href="{pub["courier"]}">CERN Courier</a>')
        if pub.get("arxiv"):
            aid = pub["arxiv"]
            links.append(
                f'<a href="#" class="bibtex-btn" '
                f"onclick=\"fetchBibtex(this, '{aid}'); return false;\">BibTeX</a>"
            )
        return "\n".join(links)

    def _render_pub(pub):
        links_html = _pub_links(pub)
        date_str = str(pub.get("date", ""))
        venue = pub.get("venue", "")
        if date_str:
            venue += f" ({date_str[:4]})"
        return f"""<li class="pub-item">
<div class="pub-title">{pub["title"]}</div>
<div class="pub-authors">{pub.get("authors", "")}</div>
<div class="pub-venue">{venue}</div>
<div class="pub-links">{links_html}</div>
</li>"""

    def _render_pub_list(items):
        if not items:
            return '<p style="color:var(--text-muted,#888);">No publications in this category yet.</p>'
        items_sorted = sorted(items, key=lambda p: str(p.get("date", "")), reverse=True)
        html = "\n".join(_render_pub(p) for p in items_sorted)
        return f'<ul class="pub-list">\n{html}\n</ul>'

    def _pub_has_type(pub, type_name):
        """Return True if pub's type field equals type_name or contains it in a list."""
        t = pub.get("type")
        if t is None:
            return False
        if isinstance(t, list):
            return type_name in t
        return t == type_name

    @env.macro
    def publications_of_type(type_name):
        """Render publications matching a specific type (string or list)."""
        matched = [p for p in pubs if _pub_has_type(p, type_name)]
        return _render_pub_list(matched)

    @env.macro
    def publications_featured():
        """Render publications with featured: true."""
        matched = [p for p in pubs if p.get("featured")]
        return _render_pub_list(matched)

    @env.macro
    def publications_all():
        """Render all publications."""
        return _render_pub_list(pubs)

    # ==================================================================
    # TALK HELPERS
    # ==================================================================

    def _render_talk(talk):
        d = talk.get("date", "")
        date_str = str(d)
        try:
            if isinstance(d, date):
                display_date = d.strftime("%b %Y")
            else:
                parts = date_str.split("-")
                months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                display_date = f"{months[int(parts[1])]} {parts[0]}"
        except (IndexError, ValueError):
            display_date = date_str

        venue = talk.get("venue", "")
        loc = talk.get("location", "")
        venue_line = f"{venue} · {loc}" if loc else venue

        link_parts = []
        if talk.get("indico"):
            url = talk["indico"]
            indico_domains = ("indico", "conference.ippp", "agenda.infn")
            label = "Indico" if any(d in url for d in indico_domains) else "Event"
            link_parts.append(f'<a href="{url}">{label}</a>')
        if talk.get("slides_url"):
            link_parts.append(f'<a href="{talk["slides_url"]}">Slides</a>')
        if talk.get("recording_url"):
            link_parts.append(f'<a href="{talk["recording_url"]}">Recording</a>')
        links_html = ""
        if link_parts:
            links_html = f'<div class="talk-links">{"".join(link_parts)}</div>'

        return f"""<div class="talk-card">
<div class="talk-date">{display_date}</div>
<div class="talk-title">{talk["title"]}</div>
<div class="talk-venue">{venue_line}</div>
{links_html}
</div>"""

    @env.macro
    def talks_by_year():
        by_year = {}
        for t in talks:
            year = str(t.get("date", ""))[:4]
            by_year.setdefault(year, []).append(t)
        html_parts = []
        for year in sorted(by_year.keys(), reverse=True):
            year_talks = sorted(by_year[year],
                                key=lambda t: str(t.get("date", "")),
                                reverse=True)
            cards = "\n".join(_render_talk(t) for t in year_talks)
            html_parts.append(
                f'<div class="sec-label">{year}</div>\n'
                f'<div class="talk-grid">\n{cards}\n</div>'
            )
        return "\n\n".join(html_parts)

    # ==================================================================
    # TEAM HELPERS
    # ==================================================================

    @env.macro
    def team_collaborators():
        """Render collaborator profile cards from team.yml."""
        collabs = team.get("collaborators", [])
        if not collabs:
            return ""
        cards = []
        for c in collabs:
            initials = "".join(w[0].upper() for w in c["name"].split()[:2])
            photo = c.get("photo", "")
            if photo:
                avatar = f'<img class="team-avatar" src="/assets/team/{photo}" alt="{c["name"]}">'
            else:
                avatar = f'<div class="team-initials">{initials}</div>'
            cards.append(f"""<div class="team-card">
{avatar}
<div class="team-name">{c["name"]}</div>
<div class="team-role">{c.get("role", "")}</div>
<div class="team-affiliation">{c.get("affiliation", "")}</div>
</div>""")
        return f'<div class="team-grid">\n{"".join(cards)}\n</div>'

    @env.macro
    def team_alumni():
        """Render alumni table from team.yml."""
        alumni = team.get("alumni", [])
        if not alumni:
            return ""
        rows = []
        for a in alumni:
            rows.append(
                f'| {a["name"]} | {a.get("role_type", "")} '
                f'| {a.get("project", "")} '
                f'| {a.get("location", "")} '
                f'| {a.get("year", "")} |'
            )
        header = "| Name | Role | Project | Location | Year |\n|------|------|---------|----------|------|\n"
        return header + "\n".join(rows)

    # ==================================================================
    # PILL HELPER
    # ==================================================================

    def _pill(label, color, url=None):
        """Render a coloured pill. Linked pills get a hover effect; unlinked don't."""
        attrs = f'class="pill" data-color="{color}"'
        if url:
            return f'<a href="{url}" {attrs}>{label}</a>'
        return f'<span {attrs}>{label}</span>'

    # ==================================================================
    # LANDING PAGE HELPERS
    # ==================================================================

    color_map = {
        "teal":    ("--teal-50",   "--teal-900",   "--teal-800"),
        "purple":  ("--purple-50", "--purple-800",  "--purple-800"),
        "coral":   ("--coral-50",  "--coral-800",   "--coral-800"),
        "blue":    ("--blue-50",   "--blue-800",    "--blue-800"),
        "amber":   ("--amber-50",  "--amber-800",   "--amber-800"),
        "red":     ("--red-50",    "--red-800",     "--red-800"),
        "green":   ("--green-50",  "--green-800",   "--green-800"),
        "pink":    ("--pink-50",   "--pink-800",    "--pink-800"),
        "gray":    ("--gray-50",   "--gray-800",    "--gray-800"),
        "slate":   ("--slate-50",  "--slate-800",   "--slate-800"),
        "indigo":  ("--indigo-50", "--indigo-800",  "--indigo-800"),
        "cyan":    ("--cyan-50",   "--cyan-800",    "--cyan-800"),
    }

    # Maps blog category slugs to pill colours.
    category_color_map = {
        "atlas":                  "teal",
        "top-quark-physics":      "amber",
        "quantum-information":    "blue",
        "machine-learning":       "purple",
        "effective-field-theory": "pink",
    }

    @env.macro
    def landing_hero():
        """Render the hero section from profile.yml."""
        name = profile.get("name", "")
        role = profile.get("role", "")
        bio = profile.get("bio", "")
        # Convert *text* to <em> for the highlight
        import re
        bio = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', bio)

        affs = profile.get("affiliations", [])
        aff_html = " · ".join(
            f'<a href="{a["url"]}">{a["name"]}</a>' for a in affs
        )

        tags = profile.get("tags", [])
        pills_html = "\n".join(
            _pill(t["label"], t.get("color", "teal"))
            for t in tags
        )

        return f"""<div class="hp-hero">
  <div class="hp-hero-row">
    <div class="hp-avatar-wrap">
      <img class="hp-avatar" src="assets/team/baptiste_ravina.jpg">
    </div>
    <div>
      <h1>{name}</h1>
      <div class="hp-sub">{role} · {aff_html}</div>
      <p class="hp-bio">{bio}</p>
      <div class="pill-row">{pills_html}</div>
    </div>
  </div>
</div>"""

    @env.macro
    def landing_featured():
        """Render featured publications. Title adapts to count."""
        featured = [p for p in pubs if p.get("featured")]
        if not featured:
            return ""
        featured.sort(key=lambda p: str(p.get("date", "")), reverse=True)
        title = "Featured result" if len(featured) == 1 else "Featured results"

        items = []
        for pub in featured:
            date_str = str(pub.get("date", ""))
            year = date_str[:4] if date_str else ""
            venue = pub.get("venue", "")
            links = _pub_links(pub)
            items.append(f"""<div class="hp-feat">
    <div class="hp-feat-lab">{venue} · {year}</div>
    <h3>{pub["title"]}</h3>
    <div class="hp-jnl">{pub.get("authors", "")}</div>
    <div class="hp-lnks">{links}</div>
  </div>""")

        return f"""<div class="hp-ey">{title}</div>
{"".join(items)}"""

    @env.macro
    def landing_research():
        """Render research cards from research.yml."""
        cards = []
        for r in research:
            c = r.get("color", "teal")
            bg, fg, _ = color_map.get(c, color_map["teal"])
            logo = r.get("logo", "")
            link = r.get("link", "#")
            cards.append(f"""<a class="hp-rc" href="{link}">
      <div class="hp-rc-i" style="background:var({bg});color:var({fg})">{logo}</div>
      <h4>{r["title"]}</h4>
      <p>{r["description"]}</p>
    </a>""")
        return f"""<div class="hp-ey">Research</div>
<div class="hp-sect">What I work on</div>
<div class="hp-rg">
{"".join(cards)}
</div>
<p style="margin-top:.5rem;"><a href="research/" style="font-size:.88rem;color:var(--teal-600);text-decoration:none;font-weight:500;">Read more about my research →</a></p>"""

    @env.macro
    def landing_career():
        """Render career timeline from career.yml."""
        items = []
        for i, c in enumerate(career):
            end = c.get("end", "")
            start = c.get("start", "")
            if end == "" and i == 0:
                date_display = f"{start} – present"
            elif end:
                date_display = f"{start} – {end}"
            else:
                date_display = start

            current_cls = " current" if i == 0 else ""
            desc = c.get("description", "")
            desc_html = f'<div class="hp-tl-desc">{desc}</div>' if desc else ""

            logo = c.get("logo", "")
            if logo:
                header_html = f"""<div class="hp-tl-header">
        <img class="hp-tl-logo" src="/assets/logos/{logo}" alt="{c['organization']}">
        <div>
          <h4>{c["title"]}</h4>
          <div class="hp-tl-o">{c["organization"]}</div>
        </div>
      </div>"""
            else:
                header_html = f"""<h4>{c["title"]}</h4>
      <div class="hp-tl-o">{c["organization"]}</div>"""

            items.append(f"""<div class="hp-tl-item{current_cls}">
      <div class="hp-tl-d">{date_display}</div>
      {header_html}
      {desc_html}
    </div>""")

        return f"""<div class="hp-ey">Career</div>
<div class="hp-sect">Where I've been</div>
<div class="hp-tl">
{"".join(items)}
</div>"""

    @env.macro
    def pub_count():
        return len([p for p in pubs if p.get("type") != "thesis"])

    @env.macro
    def talk_count():
        return len(talks)

    @env.macro
    def landing_blog(count=1):
        """Render the latest blog post(s) from docs/blog/posts/."""
        import glob
        import re

        # Check if blog plugin is enabled
        plugins = env.conf.get("plugins", {})
        if "blog" not in plugins or not plugins["blog"]:
            return ""  # Return empty string if blog is disabled

        def _cat_slug(name):
            return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

        posts_dir = os.path.join(env.project_dir, "docs", "blog", "posts")

        # Also check if directory exists
        if not os.path.isdir(posts_dir):
            return ""

        post_files = sorted(glob.glob(os.path.join(posts_dir, "*.md")), reverse=True)

        posts = []
        for pf in post_files:
            with open(pf) as f:
                content = f.read()
            parts = content.split("---")
            if len(parts) < 3:
                continue
            try:
                meta = yaml.safe_load(parts[1])
            except Exception:
                continue
            if not meta:
                continue

            # Extract title from first # heading after frontmatter
            body = "---".join(parts[2:])
            title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else os.path.basename(pf)

            # Extract summary (first paragraph after title, before <!-- more -->)
            summary = ""
            if "<!-- more -->" in body:
                intro = body.split("<!-- more -->")[0]
            else:
                intro = body
            paras = re.split(r'\n\n+', intro)
            for p in paras:
                p = p.strip()
                if p and not p.startswith("#") and not p.startswith("!"):
                    p = re.sub(r'!\[.*?\]\(.*?\)\{.*?\}', '', p).strip()
                    if p:
                        p = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', p)
                        p = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', p)
                        p = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', p)
                        summary = p
                        break

            # Build the URL slug from filename
            d = meta.get("date")
            if isinstance(d, date):
                date_obj = d
            else:
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
                except Exception:
                    date_obj = None

            if date_obj:
                slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-')
                slug = re.sub(r'-{3,}', '--', slug)
                url = f"blog/{date_obj.year}/{date_obj.month:02d}/{date_obj.day:02d}/{slug}/"
                display_date = date_obj.strftime("%B %Y")
            else:
                url = "blog/"
                display_date = ""

            categories = meta.get("categories", [])
            cat_html = "".join(
                _pill(
                    c,
                    category_color_map.get(_cat_slug(c), "teal"),
                    f"/blog/category/{_cat_slug(c)}/"
                )
                for c in categories
            )

            posts.append({
                "title": title,
                "summary": summary,
                "url": url,
                "date": display_date,
                "categories_html": cat_html,
                "date_obj": date_obj,
            })

        posts.sort(key=lambda p: p.get("date_obj") or date(1970, 1, 1), reverse=True)

        if not posts:
            return '<p style="color:var(--text-faint);">No blog posts yet.</p>'

        cards = []
        for post in posts[:count]:
            cards.append(f"""<div class="hp-blog-card" onclick="window.location.href='{post['url']}'" style="cursor:pointer;">
<div class="hp-blog-date">{post['date']}</div>
<h4>{post['title']}</h4>
<p>{post['summary']}</p>
<div class="pill-row">{post['categories_html']}</div>
</div>""")

        return f"""<hr class="hp-divider"><div style="padding-top:2rem;">
<div class="hp-ey">Latest news</div>
{"".join(cards)}
<p style="margin-top:.5rem;"><a href="blog/" style="font-size:.88rem;color:var(--teal-600);text-decoration:none;font-weight:500;">All posts →</a></p>
</div>"""