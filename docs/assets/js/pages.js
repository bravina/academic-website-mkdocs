/*
 * Interactive bits of the inner pages (markup from main.py):
 *  - .filterable: chips filter the [data-tags] items, hiding empty .filter-group
 *    sections and fading non-matching [data-tag] parts inside shown items. The choice is mirrored in the URL (?topic= / ?type=, from
 *    data-param) so filtered views can be linked, e.g. from the research page.
 *  - .pubs-page: dot timeline (hover/focus previews a paper, click jumps to it).
 *  - .copy-bib: copies the sibling .bib-src text (research page).
 * Runs on every page load, including Material's instant navigation.
 */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function setupFilter(root) {
    var chips = root.querySelectorAll(".chips button[data-f]");
    var items = root.querySelectorAll("[data-tags]");
    var groups = root.querySelectorAll(".filter-group");
    var empty = root.querySelector(".filter-empty");
    var dots = root.querySelectorAll(".pub-dot");
    var param = root.dataset.param;

    function matches(el, f) {
      return f === "all" || (" " + el.dataset.tags + " ").indexOf(" " + f + " ") !== -1;
    }

    function apply(f, updateUrl) {
      chips.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.f === f)); });
      var shown = 0;
      items.forEach(function (el) {
        var ok = matches(el, f);
        el.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector("[data-tags]:not([hidden])"); });
      // Within a shown item, fade the parts that don't match (alumni: other stints)
      root.querySelectorAll("[data-tag]").forEach(function (el) {
        el.classList.toggle("filter-dim", f !== "all" && el.dataset.tag !== f);
      });
      if (empty) empty.hidden = shown > 0;
      dots.forEach(function (d) {
        var li = document.getElementById("pub-" + d.dataset.i);
        d.classList.toggle("dim", !!li && li.hidden);
      });
      root.dataset.current = f;
      if (updateUrl && param) {
        var url = new URL(window.location.href);
        if (f === "all") url.searchParams.delete(param);
        else url.searchParams.set(param, f);
        history.replaceState(history.state, "", url);
      }
    }

    root.querySelector(".chips").addEventListener("click", function (e) {
      var b = e.target.closest("button[data-f]");
      if (b) apply(b.dataset.f, true);
    });

    var wanted = param && new URLSearchParams(window.location.search).get(param);
    var known = Array.prototype.some.call(chips, function (b) { return b.dataset.f === wanted; });
    apply(known ? wanted : "all", false);

    return apply;
  }

  function setupTimeline(root, apply) {
    var years = root.querySelector(".pub-years");
    var peek = root.querySelector(".pub-peek");
    if (!years || !peek) return;

    function show(dot) {
      var li = document.getElementById("pub-" + dot.dataset.i);
      if (!li) return;
      var title = li.querySelector(".pub-title").cloneNode(true);
      var star = title.querySelector(".pub-star");
      if (star) star.remove();
      var venue = li.querySelector(".pub-venue em");
      var year = li.closest(".filter-group").querySelector(".yr-h");
      peek.innerHTML = "";
      var b = document.createElement("b");
      b.innerHTML = title.innerHTML;
      peek.appendChild(b);
      peek.appendChild(document.createElement("br"));
      peek.appendChild(document.createTextNode(
        (venue ? venue.textContent : "") + (year ? " · " + year.textContent : "")));
    }

    years.addEventListener("mouseover", function (e) {
      var d = e.target.closest(".pub-dot");
      if (d) show(d);
    });
    years.addEventListener("focusin", function (e) {
      var d = e.target.closest(".pub-dot");
      if (d) show(d);
    });
    years.addEventListener("click", function (e) {
      var d = e.target.closest(".pub-dot");
      if (!d) return;
      show(d);
      var li = document.getElementById("pub-" + d.dataset.i);
      if (!li) return;
      if (li.hidden) apply("all", true);
      li.scrollIntoView({ behavior: reduceMotion.matches ? "auto" : "smooth", block: "center" });
      li.classList.add("flash");
      setTimeout(function () { li.classList.remove("flash"); }, 1400);
    });
  }

  function setupCopyBib(btn) {
    var src = btn.closest(".callout").querySelector(".bib-src");
    if (!src) return;
    btn.addEventListener("click", function () {
      function done(text) {
        btn.textContent = text;
        setTimeout(function () { btn.textContent = "Copy BibTeX"; }, 1600);
      }
      try {
        navigator.clipboard.writeText(src.textContent.trim())
          .then(function () { done("Copied"); }, function () { done("Copy failed"); });
      } catch (err) {
        done("Copy failed");
      }
    });
  }

  function init() {
    document.querySelectorAll(".filterable").forEach(function (root) {
      var apply = setupFilter(root);
      if (root.classList.contains("pubs-page")) setupTimeline(root, apply);
    });
    document.querySelectorAll(".copy-bib").forEach(setupCopyBib);
  }

  if (typeof document$ !== "undefined") document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
