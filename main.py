"""
MkDocs Macros plugin — loads all YAML data and provides rendering macros.
"""
import yaml
import os
import re
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
        if pub.get("rivet"):
            links.append(f'<a href="{pub["rivet"]}">Rivet</a>')
        if pub.get("atlas_url"):
            links.append(f'<a href="{pub["atlas_url"]}">ATLAS</a>')
        if pub.get("briefing"):
            links.append(f'<a href="{pub["briefing"]}">Briefing</a>')
        if pub.get("courier"):
            links.append(f'<a href="{pub["courier"]}">CERN Courier</a>')
        if pub.get("git"):
            links.append(f'<a href="{pub["git"]}">Code on Git</a>')
        # BibTeX button: prefer arXiv, fall back to InspireHEP literature ID
        if pub.get("arxiv"):
            aid = pub["arxiv"]
            links.append(
                f'<a href="javascript:void(0)" class="bibtex-btn" '
                f"onclick=\"fetchBibtex(this, '{aid}', null)\">BibTeX</a>"
            )
        elif pub.get("inspirehep"):
            iid = pub["inspirehep"]
            links.append(
                f'<a href="javascript:void(0)" class="bibtex-btn" '
                f"onclick=\"fetchBibtex(this, null, '{iid}')\">BibTeX</a>"
            )
            links.append(f'<a href="https://inspirehep.net/literature/{iid}">INSPIRE</a>')
        return "\n".join(links)

    # Topic of each publications.yml `type`: (label, colour). The colour names a
    # --topic-* token (dots, chips, tags) in custom.css. Chips follow this order.
    PUB_TYPES = {
        "top":         ("Top quark physics",        "amber"),
        "quantum":     ("Quantum information",      "blue"),
        "search":      ("Searches for new physics", "indigo"),
        "ml":          ("Machine learning",         "purple"),
        "software":    ("Software",                 "cyan"),
        "proceedings": ("Proceedings",              "gray"),
        "thesis":      ("Thesis",                   "coral"),
    }

    def _pub_types(pub):
        t = pub.get("type") or []
        return t if isinstance(t, list) else [t]

    def _pubs_sorted():
        return sorted(pubs, key=lambda p: str(p.get("date", "")), reverse=True)

    def _chips(options, label):
        """Filter chips: options are (key, label, count, colour-or-None)."""
        buttons = "".join(
            f'<button type="button" data-f="{k}" aria-pressed="{str(k == "all").lower()}">'
            + (f'<i style="background:var(--topic-{c})"></i>' if c else "")
            + f'{n} <small>{cnt}</small></button>'
            for k, n, cnt, c in options if cnt
        )
        return f'<div class="chips" role="group" aria-label="{label}">{buttons}</div>'

    def _pub_count(type_name):
        return sum(type_name in _pub_types(p) for p in pubs)

    @env.macro
    def publications_page():
        """Publications page: topic chips, dot timeline (one dot per entry,
        ringed if featured) and one list grouped by year. Filtering, the
        hover preview and ?topic=<type> are handled by assets/js/pages.js."""
        items = _pubs_sorted()
        years = [int(str(p.get("date", "0"))[:4]) for p in items]
        chips = _chips(
            [("all", "All", len(items), None)]
            + [(k, n, _pub_count(k), c) for k, (n, c) in PUB_TYPES.items()],
            "Filter by topic",
        )

        cols = []
        for y in range(min(years), max(years) + 1):
            dots = []
            for i, p in enumerate(items):
                if years[i] != y:
                    continue
                types = _pub_types(p)
                c = PUB_TYPES.get(types[0], ("", "gray"))[1] if types else "gray"
                star = " star" if p.get("featured") else ""
                venue = str(p.get("venue", "")).replace('"', "&quot;")
                dots.append(
                    f'<button type="button" class="pub-dot{star}" data-i="{i}" '
                    f'style="--c:var(--topic-{c})" aria-label="{venue}, {y}"></button>'
                )
            cols.append(f'<div class="pub-yr"><span>’{str(y)[2:]}</span>{"".join(dots)}</div>')
        strip = (
            f'<div class="pub-strip"><div class="pub-years" '
            f'style="grid-template-columns:repeat({len(cols)},minmax(34px,1fr))">{"".join(cols)}</div></div>'
        )

        groups = {}
        for i, p in enumerate(items):
            groups.setdefault(years[i], []).append((i, p))
        sections = []
        for y in sorted(groups, reverse=True):
            lis = "\n".join(_render_pub(p, i) for i, p in groups[y])
            sections.append(
                f'<section class="filter-group"><h2 class="yr-h">{y}</h2>\n'
                f'<ul class="pub-list">\n{lis}\n</ul></section>'
            )
        return (
            f'<div class="filterable pubs-page" data-param="topic">{chips}{strip}'
            f'<div class="pub-peek" aria-live="polite"></div>'
            + "\n".join(sections)
            + '<p class="filter-empty" hidden>No entries for this topic.</p></div>'
        )

    def _render_pub(pub, i):
        types = _pub_types(pub)
        tags = "".join(
            f'<span class="pub-tag"><i style="background:var(--topic-{PUB_TYPES[t][1]})"></i>{PUB_TYPES[t][0]}</span>'
            for t in types if t in PUB_TYPES
        )
        star = '<span class="pub-star" title="Highlight">★</span>' if pub.get("featured") else ""
        return f"""<li class="pub-item" id="pub-{i}" data-tags="{' '.join(types)}">
<div class="pub-title">{pub["title"]}{star}</div>
<div class="pub-authors">{pub.get("authors", "")}</div>
<div class="pub-venue"><em>{pub.get("venue", "")}</em>{tags}</div>
<div class="pub-links">{_pub_links(pub)}</div>
</li>"""

    # ==================================================================
    # TALK HELPERS
    # ==================================================================

    # talks.yml `type` → chip label (plural) and tag label. Chips follow this order.
    TALK_TYPES = {
        "seminar":    ("Seminars",      "Seminar"),
        "conference": ("Conferences",   "Conference"),
        "workshop":   ("Workshops",     "Workshop"),
        "atlas":      ("ATLAS meetings", "ATLAS meeting"),
    }
    MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def _render_talk(talk):
        try:
            month = MONTHS[int(str(talk.get("date", ""))[5:7])]
        except (IndexError, ValueError):
            month = ""

        venue = talk.get("venue", "")
        loc = talk.get("location", "")
        venue_line = f"{venue} · {loc}" if loc else venue
        ttype = talk.get("type", "")
        tag = (f'<span class="talk-type" data-type="{ttype}">{TALK_TYPES[ttype][1]}</span>'
               if ttype in TALK_TYPES else "")

        link_parts = []
        if talk.get("indico"):
            url = talk["indico"]
            indico_domains = ("indico", "conference.ippp", "agenda.infn")
            label = "Indico" if any(d in url for d in indico_domains) else "Event"
            link_parts.append(f'<a href="{url}">{label}</a>')
        if talk.get("slides_url"):
            link_parts.append(f'<a href="{talk["slides_url"]}">Slides</a>')
        if talk.get("recording_url"):
            link_parts.append(f'<a class="talk-rec" href="{talk["recording_url"]}">Recording</a>')

        tags = ttype + (" recorded" if talk.get("recording_url") else "")
        return f"""<div class="talk-row" data-tags="{tags.strip()}">
<div class="talk-date">{month}</div>
<div><div class="talk-title">{talk["title"]}</div><div class="talk-venue">{tag}{venue_line}</div></div>
<div class="talk-links">{"".join(link_parts)}</div>
</div>"""

    @env.macro
    def talks_page():
        """Talks page: type chips and compact rows grouped by year.
        Filtering is handled by assets/js/pages.js."""
        options = [("all", "All", len(talks), None)]
        options += [(k, plural, sum(t.get("type") == k for t in talks), None)
                    for k, (plural, _) in TALK_TYPES.items()]
        options.append(("recorded", "With recording", sum(bool(t.get("recording_url")) for t in talks), None))

        by_year = {}
        for t in talks:
            by_year.setdefault(str(t.get("date", ""))[:4], []).append(t)
        sections = []
        for year in sorted(by_year, reverse=True):
            rows = "\n".join(_render_talk(t) for t in
                             sorted(by_year[year], key=lambda t: str(t.get("date", "")), reverse=True))
            sections.append(f'<section class="filter-group"><h2 class="yr-h">{year}</h2>\n{rows}\n</section>')
        return (
            f'<div class="filterable talks-page" data-param="type">{_chips(options, "Filter by type")}'
            + "\n".join(sections)
            + '<p class="filter-empty" hidden>No talks of this type.</p></div>'
        )

    # ==================================================================
    # TEAM HELPERS
    # ==================================================================

    def _person_card(p):
        photo = p.get("photo", "")
        if photo:
            avatar = f'<img class="person-av" src="/assets/team/{photo}" alt="" loading="lazy">'
        else:
            initials = "".join(w[0].upper() for w in p["name"].split()[:2])
            avatar = f'<div class="person-av" aria-hidden="true">{initials}</div>'
        affiliation = p.get("affiliation", "")
        return f"""<div class="person">{avatar}<div>
<div class="person-name">{p["name"]}</div>
<div class="person-role">{p.get("role", "")}</div>
<div class="person-aff">{affiliation}</div>
</div></div>"""

    @env.macro
    def team_students():
        """Current students from team.yml, plus a card inviting new students
        that links to the email address in profile.yml."""
        cards = [_person_card(s) for s in team.get("students") or []]
        email = profile.get("email", "")
        cards.append(f"""<div class="person person-open"><div class="person-av" aria-hidden="true">+</div><div>
<div class="person-name">New project?</div>
<div class="person-role">BSc, MSc, PhD</div>
<div class="person-aff"><a href="mailto:{email}?subject=Student%20project">Get in touch</a></div>
</div></div>""")
        return f'<div class="people people-students">{"".join(cards)}</div>'

    @env.macro
    def team_collaborators():
        """Collaborator cards from team.yml."""
        cards = [_person_card(c) for c in team.get("collaborators") or []]
        return f'<div class="people">{"".join(cards)}</div>' if cards else ""

    def _year_sort_key(a):
        year_str = str(a.get("year", "0"))
        parts = year_str.replace("–", "-").split("-")
        # Use last part if compound (e.g. "2022-23" → 23 → expand to 2023), else the year itself
        if len(parts) > 1:
            suffix = parts[-1]
            prefix = parts[0][:2]  # e.g. "20"
            return int(prefix + suffix)
        return int(parts[0])

    @env.macro
    def team_alumni():
        """Render the alumni table from team.yml: one row per person.

        People with several stints (an `entries` list, e.g. BSc then MSc)
        get one line per stint, oldest first, so the row reads as a progression.
        "Next position" is taken from the most recent stint. Rows are ordered
        by each person's most recent year. On narrow screens the CSS turns
        rows into stacked cards (see .alumni-table in custom.css).

        Chips above the table filter by role_type (assets/js/pages.js, ?degree=):
        a person matches if any of their stints has that role, and their other
        stints are faded.
        """
        alumni = team.get("alumni", [])
        if not alumni:
            return ""

        people = []
        for a in alumni:
            entries = a.get("entries") or [a]
            # Oldest first. team.yml lists stints newest first, so reverse before the
            # (stable) sort: same-year stints then stay in chronological order,
            # e.g. Steffen Korn: PhD 2023, then Postdoc 2023.
            entries = sorted(reversed(entries), key=_year_sort_key)
            people.append({
                "name": a["name"],
                "entries": entries,
                "next": entries[-1].get("next_position", ""),
                "latest": _year_sort_key(entries[-1]),
            })
        people.sort(key=lambda p: p["latest"], reverse=True)

        def slug(role):
            return re.sub(r"[^a-z0-9]+", "-", role.lower()).strip("-")

        # Chips: degrees first, then the other role types in order of appearance
        roles = []
        for p in people:
            for e in p["entries"]:
                r = e.get("role_type", "")
                if r and r not in roles:
                    roles.append(r)
        first = ["BSc", "MSc", "PhD", "Postdoc"]
        roles.sort(key=lambda r: first.index(r) if r in first else len(first))
        # Counts are projects (stints), so the role counts add up to "All"
        stints = [e for p in people for e in p["entries"]]
        chips = _chips(
            [("all", "All", len(stints), None)]
            + [(slug(r), r, sum(e.get("role_type") == r for e in stints), None) for r in roles],
            "Filter by role",
        )

        rows = []
        for p in people:
            tags = " ".join(dict.fromkeys(slug(e.get("role_type", "")) for e in p["entries"]))
            stints = "".join(
                f'<div class="alum-stint" data-tag="{slug(e.get("role_type", ""))}">'
                f'<span class="alum-role">{e.get("role_type", "")}</span> '
                f'<span class="alum-project">{e.get("project", "")}</span> '
                f'<span class="alum-meta">{e.get("location", "")} · {e.get("year", "")}</span>'
                f'</div>'
                for e in p["entries"]
            )
            nxt = p["next"]
            next_html = f'<span class="alum-next-label">Next: </span>{nxt}' if nxt else ""
            rows.append(
                f'<tr data-tags="{tags}"><td class="alum-name">{p["name"]}</td>'
                f'<td class="alum-stints">{stints}</td>'
                f'<td class="alum-next">{next_html}</td></tr>'
            )
        return (
            f'<div class="filterable alumni" data-param="degree">{chips}'
            '<table class="alumni-table">'
            '<thead><tr><th>Name</th><th>Project</th><th>Next position</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>'
            '<p class="filter-empty" hidden>No alumni with this role.</p></div>'
        )

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

    # Blog category slug -> pill colour, defined once in mkdocs.yml (extra.blog_category_colors)
    category_color_map = (env.conf.get("extra") or {}).get("blog_category_colors") or {}

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
        # Each part is an unbreakable item; the line can only wrap between
        # items, and home.js hides the "·" of an item that starts a new line.
        sub_items = [f'<span class="hp-sub-item">{role}</span>'] + [
            f'<span class="hp-sub-item"><span class="hp-sub-sep" aria-hidden="true">· </span>'
            f'<a href="{a["url"]}">{a["name"]}</a></span>'
            for a in affs
        ]
        sub_html = " ".join(sub_items)

        tags = profile.get("tags", [])
        pills_html = "\n".join(
            _pill(t["label"], t.get("color", "teal"))
            for t in tags
        )

        # Event display (animated by docs/assets/js/home.js): the portrait sits
        # at the interaction point of a stylised detector drawn on the canvas.
        return f"""<div class="hp-hero">
  <div class="hp-hero-row">
    <div class="hp-avatar-wrap">
      <div class="hp-evd">
        <canvas class="hp-evd-canvas" tabindex="0" role="img" title="Click for another collision" aria-label="Animated cross-section of a particle detector showing a simulated top-quark pair collision. Click for another collision."></canvas>
        <img class="hp-avatar" src="assets/team/baptiste_ravina.jpg" alt="{name}">
      </div>
      <div class="hp-evd-cap nomath" aria-hidden="true"></div>
    </div>
    <div>
      <h1>{name}</h1>
      <div class="hp-sub">{sub_html}</div>
      <p class="hp-bio">{bio}</p>
      <div class="pill-row">{pills_html}</div>
    </div>
  </div>
</div>"""

    @env.macro
    def landing_featured():
        """Homepage spotlight: one featured result at a time, with tabs.

        Uses the optional headline / summary / figure / short_title fields of
        featured entries in publications.yml (see the comment at its top);
        rotation and tabs are driven by assets/js/home.js (Spotlight).
        """
        featured = [p for p in pubs if p.get("featured")]
        if not featured:
            return ""
        # Numbered entries first (1, 2, ...), then `featured: true` ones, newest first
        featured.sort(key=lambda p: str(p.get("date", "")), reverse=True)
        featured.sort(key=lambda p: p["featured"] if type(p["featured"]) is int else float("inf"))
        title = "Featured result" if len(featured) == 1 else "Featured results"

        slides, tabs = [], []
        for i, pub in enumerate(featured):
            year = str(pub.get("date", ""))[:4]
            headline = pub.get("headline") or pub["title"]
            short = pub.get("short_title") or headline
            if pub.get("arxiv"):
                url = f'https://arxiv.org/abs/{pub["arxiv"]}'
            elif pub.get("doi"):
                url = f'https://doi.org/{pub["doi"]}'
            else:
                url = pub.get("atlas_url", "publications/")
            summary = f'<p>{pub["summary"]}</p>' if pub.get("summary") else ""
            fig = ""
            if pub.get("figure"):
                fig = (f'<div class="hp-spot-fig"><img src="assets/figures/{pub["figure"]}" '
                       f'alt="Figure from: {pub["title"]}" loading="lazy"></div>')
            on = i == 0
            slides.append(f"""<article class="hp-spot-slide{' on' if on else ''}{'' if fig else ' no-fig'}" id="hp-spot-{i}" role="tabpanel" aria-labelledby="hp-spot-tab-{i}">
{fig}<div class="hp-spot-story">
<span class="hp-spot-lab">{pub.get("venue", "")} · {year}</span>
<h3>{headline}</h3>{summary}
<a class="hp-spot-go" href="{url}">Read the paper →</a>
</div>
</article>""")
            tabs.append(f'<button type="button" class="hp-spot-tab" role="tab" id="hp-spot-tab-{i}" '
                        f'aria-controls="hp-spot-{i}" aria-selected="{str(on).lower()}" tabindex="{0 if on else -1}">'
                        f'<span class="hp-spot-bar" aria-hidden="true"></span>{short}<small>{year}</small></button>')

        tablist = (f'<div class="hp-spot-tabs" role="tablist" aria-label="Choose a result" '
                   f'style="--n:{len(tabs)}">{"".join(tabs)}</div>'
                   if len(tabs) > 1 else "")
        return f"""<div class="hp-sect">{title}</div>
<section class="hp-spot" aria-roledescription="carousel" aria-label="{title}">
<div class="hp-spot-stage">
{"".join(slides)}
</div>
{tablist}
</section>
<p class="hp-spot-all"><a href="publications/">All publications →</a></p>"""

    @env.macro
    def landing_research():
        """Render research cards from research.yml."""
        cards = []
        for r in research:
            c = r.get("color", "teal")
            bg, fg, _ = color_map.get(c, color_map["teal"])
            logo = r.get("logo", "")
            link = r.get("link", "#")
            # Optional topic animation, inlined so it can use the page's colours
            # and react to hover: data/card-anims/<key>.svg (styles in custom.css 6d,
            # playback in home.js).
            anim = ""
            anim_path = os.path.join(data_dir, "card-anims", f'{r.get("key", "")}.svg')
            if r.get("key") and os.path.exists(anim_path):
                with open(anim_path) as f:
                    anim = f.read().strip()
            cards.append(f"""<a class="hp-rc" href="{link}">
      <div class="hp-rc-top"><div class="hp-rc-i" style="background:var({bg});color:var({fg})">{logo}</div>{anim}</div>
      <h4>{r["title"]}\u2060<span class="hp-rc-go" aria-hidden="true">→</span></h4>
      <p>{r["description"]}</p>
    </a>""")
        return f"""<div class="hp-sect">What I work on</div>
<div class="hp-rg">
{"".join(cards)}
</div>
<p style="margin-top:.5rem;"><a href="research/" style="font-size:.88rem;color:var(--teal-600);text-decoration:none;font-weight:500;">Read more about my research →</a></p>"""

    # ------------------------------------------------------------------
    # Research page: the topics in research.yml (matched by `key`) give
    # the jump cards, the heading icons and the "Papers on this topic" links.
    # ------------------------------------------------------------------

    def _research_entry(key):
        for r in research:
            if r.get("key") == key:
                return r
        raise KeyError(f"research.yml has no entry with key '{key}'")

    def _research_icon(r):
        bg, fg, _ = color_map.get(r.get("color", "teal"), color_map["teal"])
        return (f'<span class="sec-ico" aria-hidden="true" '
                f'style="background:var({bg});color:var({fg})">{r.get("logo", "")}</span>')

    @env.macro
    def research_icon(key):
        """Topic icon for a research.md heading: ## {{ research_icon('top') }} Title {#anchor}"""
        return _research_icon(_research_entry(key))

    @env.macro
    def research_cards():
        """Jump cards to each topic on the research page, with paper counts."""
        cards = []
        for r in research:
            anchor = "#" + r.get("link", "").split("#", 1)[-1]
            n = _pub_count(r["pubs"]) if r.get("pubs") else 0
            count = f'<span class="sec-card-n">{n} paper{"" if n == 1 else "s"}</span>' if n else ""
            cards.append(f'<a class="sec-card" href="{anchor}">{_research_icon(r)}'
                         f'<span class="sec-card-t">{r["title"]}</span>{count}</a>')
        return f'<nav class="sec-cards" aria-label="Research topics">{"".join(cards)}</nav>'

    @env.macro
    def research_papers(key):
        """Link to the publications page filtered to this topic."""
        t = _research_entry(key).get("pubs", "")
        n = _pub_count(t)
        if not n:
            return ""
        return (f'<p class="sec-foot"><a class="to-pubs" href="../publications/?topic={t}">'
                f'Papers on this topic ({n}) →</a></p>')

    @env.macro
    def landing_career(visible=5):
        """Render career timeline from career.yml.

        The first `visible` entries are shown; the rest fold into a
        <details> element. docs/assets/js/home.js fills the timeline line
        and lights up each entry as the visitor scrolls past it.
        """
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

        shown, folded = items[:visible], items[visible:]
        earlier = ""
        if folded:
            earlier = f"""<details class="hp-tl-earlier">
<summary>Earlier positions and education ({len(folded)})</summary>
{"".join(folded)}
</details>"""

        return f"""<div class="hp-sect">Where I've been</div>
<div class="hp-tl">
<div class="hp-tl-fill" aria-hidden="true"></div>
{"".join(shown)}{earlier}
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
        # Material registers the plugin as "material/blog"
        if not any(name.split("/")[-1] == "blog" for name in plugins):
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
<div class="hp-sect">Latest news</div>
{"".join(cards)}
<p style="margin-top:.5rem;"><a href="blog/" style="font-size:.88rem;color:var(--teal-600);text-decoration:none;font-weight:500;">All posts →</a></p>
</div>"""
