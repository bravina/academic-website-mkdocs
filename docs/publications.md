---
title: Publications
description: Selected publications with links and BibTeX export
hide:
  - navigation
---

Full list on [INSPIRE-HEP](https://inspirehep.net/authors/1794058) and [ORCID](https://orcid.org/0000-0002-1622-6640). Click **BibTeX** to export citations.

## Highlights

{{ publications_featured() }}

## Top quark physics

{{ publications_of_type('top') }}

## BSM searches

{{ publications_of_type('search') }}

## Machine learning

{{ publications_of_type('ml') }}

## Conference proceedings

{{ publications_of_type('proceedings') }}

## Thesis

{{ publications_of_type('thesis') }}

## All ATLAS publications

{{ publications_from_atlas() }}

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
async function fetchBibtex(el, arxivId) {
  var modal = document.getElementById('bibtex-modal');
  var pre = document.getElementById('bibtex-text');
  modal.classList.add('active');
  pre.textContent = 'Loading from INSPIRE-HEP...';
  try {
    var resp = await fetch('https://inspirehep.net/api/arxiv/' + arxivId + '?format=bibtex');
    if (resp.ok) {
      pre.textContent = await resp.text();
    } else {
      var resp2 = await fetch('https://inspirehep.net/api/literature?q=find+eprint+' + arxivId + '&format=bibtex');
      pre.textContent = resp2.ok ? await resp2.text() : 'Could not fetch BibTeX. Try INSPIRE-HEP directly.';
    }
  } catch (e) {
    pre.textContent = 'Network error. Visit https://inspirehep.net/literature?q=' + arxivId;
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
