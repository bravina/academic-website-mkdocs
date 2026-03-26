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

    @env.macro
    def publications_of_type(type_name):
        """Render publications matching a specific type."""
        matched = [p for p in pubs if p.get("type") == type_name]
        return _render_pub_list(matched)

    @env.macro
    def publications_featured():
        """Render publications with featured: true."""
        matched = [p for p in pubs if p.get("featured")]
        return _render_pub_list(matched)

    @env.macro
    def publications_from_atlas():
        """Render all publications with 'ATLAS' in the authors field."""
        matched = [p for p in pubs if "ATLAS" in p.get("authors", "")]
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
            link_parts.append(f'<a href="{talk["indico"]}">Indico</a>')
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
                avatar = f'<img class="team-avatar" src="assets/team/{photo}" alt="{c["name"]}">'
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
    # LANDING PAGE HELPERS
    # ==================================================================

    color_map = {
        "teal":   ("--teal-50", "--teal-900", "--teal-800"),
        "purple": ("--purple-50", "--purple-800", "--purple-800"),
        "coral":  ("--coral-50", "--coral-800", "--coral-800"),
        "blue":   ("--blue-50", "--blue-800", "--blue-800"),
    }

    @env.macro
    def landing_hero():
        """Render the hero section from profile.yml."""
        name = profile.get("name", "")
        role = profile.get("role", "")
        email = profile.get("email", "")
        bio = profile.get("bio", "")
        # Convert *text* to <em> for the highlight
        import re
        bio = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', bio)

        affs = profile.get("affiliations", [])
        aff_html = " · ".join(
            f'<a href="{a["url"]}">{a["name"]}</a>' for a in affs
        )

        tags = profile.get("tags", [])
        pills = []
        for t in tags:
            c = t.get("color", "teal")
            pills.append(f'<span class="hp-pill hp-pill-{c[0]}">{t["label"]}</span>')
        pills_html = "\n".join(pills)

        return f"""<div class="hp-hero">
  <div class="hp-hero-row">
    <div class="hp-avatar-placeholder">{"".join(w[0] for w in name.split()[:2])}</div>
    <div>
      <h1>{name}</h1>
      <div class="hp-sub">{role} · {aff_html}</div>
      <p class="hp-bio">{bio}</p>
      <div class="hp-pills">{pills_html}</div>
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
            date_display = f"{start} – {'present' if not end else end}" if end != "" or i == 0 else start
            if end == "" and i == 0:
                date_display = f"{start} – present"
            elif end:
                date_display = f"{start} – {end}"
            else:
                date_display = start

            current_cls = " current" if i == 0 else ""
            desc = c.get("description", "")
            desc_html = f'<div class="hp-tl-desc">{desc}</div>' if desc else ""

            items.append(f"""<div class="hp-tl-item{current_cls}">
      <div class="hp-tl-d">{date_display}</div>
      <h4>{c["title"]}</h4>
      <div class="hp-tl-o">{c["organization"]}</div>
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
