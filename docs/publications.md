---
title: Publications
description: Selected publications with links and BibTeX export
hide:
  - navigation
---

Full list on [INSPIRE-HEP](https://inspirehep.net/authors/1495662) and [ORCID](https://orcid.org/0000-0002-1622-6640).

## Highlights

{{ publications_featured() }}

## Top quark physics

{{ publications_of_type('top') }}

## Quantum information

{{ publications_of_type('quantum') }}

## Searches for New Physics

{{ publications_of_type('search') }}

## Machine learning

{{ publications_of_type('ml') }}

## Conference proceedings

{{ publications_of_type('proceedings') }}

## Software and algorithms

{{ publications_of_type('software') }}

## Thesis

{{ publications_of_type('thesis') }}

---

<div class="bibtex-modal" id="bibtex-modal" onclick="if(event.target===this)closeBibtex()">
<div class="bibtex-content">
<button class="bibtex-close" onclick="closeBibtex()">&times;</button>
<h3 style="margin:0 0 0.5rem;">BibTeX</h3>
<pre id="bibtex-text">Loading...</pre>
<button class="bibtex-copy" onclick="copyBibtex()">Copy to clipboard</button>
</div>
</div>

<script>
async function fetchBibtex(el, arxivId, inspireId) {
  var modal = document.getElementById('bibtex-modal');
  var pre = document.getElementById('bibtex-text');
  modal.classList.add('active');
  pre.textContent = 'Loading from INSPIRE-HEP...';
  try {
    var resp, url;
    if (arxivId) {
      // arXiv path: direct lookup, then fallback query
      resp = await fetch('https://inspirehep.net/api/arxiv/' + arxivId + '?format=bibtex');
      if (!resp.ok) {
        resp = await fetch('https://inspirehep.net/api/literature?q=find+eprint+' + arxivId + '&format=bibtex');
      }
    } else if (inspireId) {
      // InspireHEP literature ID path: direct lookup by ID
      resp = await fetch('https://inspirehep.net/api/literature/' + inspireId + '?format=bibtex');
    } else {
      pre.textContent = 'No arXiv or InspireHEP ID available for this entry.';
      return;
    }
    pre.textContent = resp.ok ? await resp.text() : 'Could not fetch BibTeX. Try INSPIRE-HEP directly.';
  } catch (e) {
    var id = arxivId || inspireId;
    pre.textContent = 'Network error. Visit https://inspirehep.net/literature?q=' + id;
  }
}
function closeBibtex() { document.getElementById('bibtex-modal').classList.remove('active'); }
function copyBibtex() {
  var text = document.getElementById('bibtex-text').textContent;
  navigator.clipboard.writeText(text).then(function() {
    var btn = document.querySelector('.bibtex-copy');
    btn.textContent = 'Copied!';
    setTimeout(function() { btn.textContent = 'Copy to clipboard'; }, 1500);
  });
}
</script>
