"""
hooks.py — MkDocs hook to fix git-revision-date-localized for data-driven pages.

Some pages are generated from YAML data files (e.g. talks.md from data/talks.yml).
The git-revision-date-localized plugin only tracks changes to the .md file itself,
so it misses updates made to the underlying data files.

This hook fires during on_page_context, which runs after all plugins (including
git-revision-date-localized) have processed the page. It overwrites the revision
date meta with the most recent git commit date across all data files mapped to
that page.

Register in mkdocs.yml:
    hooks:
      - hooks.py
"""

import os
import subprocess
from datetime import datetime


# Maps each YAML data file to the .md page that renders it.
# Add or adjust entries here if pages or data files are renamed.
DATA_PAGE_MAP = {
    "career.yml":       "career.md",
    "profile.yml":      "index.md",
    "publications.yml": "publications.md",
    "research.yml":     "research.md",
    "talks.yml":        "talks.md",
    "team.yml":         "team.md",
}


def _latest_git_mtime(paths):
    """Return the most recent git commit timestamp (--format=%ci) across all given paths.

    Returns a string like '2026-04-07 12:27:51 +0200', or None if no git history
    is found for any of the paths.
    """
    latest = None
    for path in paths:
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci", "--", path],
                capture_output=True,
                text=True,
            )
            ts = result.stdout.strip()
            if ts:
                latest = ts if latest is None else max(latest, ts)
        except Exception as e:
            print(f"[hooks] git error for {path}: {e}")
    return latest

def _format_date(ts):
    """Format a git --format=%ci timestamp to match git-revision-date-localized's
    default 'date' format, e.g. 'April 2, 2026'."""
    dt = datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%B %-d, %Y")  # e.g. "April 2, 2026"

def on_page_context(context, page, config, **kwargs):
    """Overwrite git_revision_date_localized in page.meta with the latest commit
    date of the corresponding data file(s), if any.

    This fires after all plugins have run, ensuring our value takes precedence
    over what git-revision-date-localized set based on the .md file alone.
    """
    page_file = page.file.src_path  # e.g. "talks.md"

    # Find data files mapped to this page
    data_dir = os.path.join(os.path.dirname(config["config_file_path"]), "data")
    data_files = [
        os.path.join(data_dir, yml)
        for yml, md in DATA_PAGE_MAP.items()
        if md == page_file
    ]

    if not data_files:
        return  # Page has no associated data files, leave date untouched

    latest = _latest_git_mtime(data_files)
    if latest:
        page.meta["git_revision_date_localized"] = _format_date(latest)
