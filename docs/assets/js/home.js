/*
 * home.js — landing-page interactions
 *
 * 1. Event-display hero: the portrait sits at the interaction point of a
 *    stylised detector (tracker, EM + hadronic calorimeters, muon chambers).
 *    A simulated ttbar -> (b l nu)(b l nu) event is drawn every few seconds;
 *    clicking the canvas draws a new one. Pauses when off screen or when the
 *    tab is hidden; draws a single still event under prefers-reduced-motion.
 * 2. Career timeline: the vertical line fills as the visitor scrolls and each
 *    position "lights up" once reached. Without JS the timeline renders fully lit.
 *
 * Colours come from the --evd-* tokens in custom.css (light + slate schemes).
 * Re-initialised on every page load via Material's document$ (navigation.instant).
 */
(function () {
  "use strict";

  var TAU = Math.PI * 2;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function clamp(x) { return Math.max(0, Math.min(1, x)); }
  function easeOut(x) { return 1 - Math.pow(1 - x, 3); }
  function rnd(a, b) { return a + Math.random() * (b - a); }
  function wrapAngle(a) { return ((a % TAU) + TAU) % TAU; }
  function gauss() {
    var u = 0, v = 0;
    while (!u) u = Math.random();
    while (!v) v = Math.random();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v);
  }
  function angleBetween(a, b) { return Math.abs(Math.atan2(Math.sin(a - b), Math.cos(a - b))); }

  /* ================================================================
     1. EVENT DISPLAY
     ================================================================ */

  // Detector layers, as fractions of the canvas radius. The portrait
  // (.hp-avatar, 50% of the box width) covers everything inside trkIn.
  var L = {
    trkIn: 0.51, trkOut: 0.645,
    emIn: 0.665, emOut: 0.75,
    hadIn: 0.765, hadOut: 0.87,
    muIn: 0.892, muOut: 0.978
  };
  var N_EM = 64, N_HAD = 32, N_MU = 16, MU_GAP = 0.05;

  // Event lifecycle (ms)
  var T_GROW = 750, T_CELLS = 350, T_HOLD = 4700, T_FADE = 600;

  function EventDisplay(box) {
    this.box = box;
    this.canvas = box.querySelector("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.caption = box.parentNode.querySelector(".hp-evd-cap");
    this.W = 0; this.R = 0;
    this.colors = {};
    this.ev = null;
    this.visible = true;
    this.alive = true;
    this.abort = new AbortController();

    var self = this, signal = this.abort.signal;
    this.readColors();
    this.resize();
    this.newEvent();

    this.resizeObs = new ResizeObserver(function () { self.resize(); });
    this.resizeObs.observe(this.canvas);

    this.visObs = new IntersectionObserver(function (entries) {
      var was = self.visible;
      self.visible = entries[0].isIntersecting;
      // Coming back into view: restart the current event rather than jump to its end
      if (self.visible && !was && self.ev) self.ev.t0 = performance.now() - T_GROW;
    });
    this.visObs.observe(this.canvas);

    // Material toggles data-md-color-scheme on <body>
    this.themeObs = new MutationObserver(function () { self.readColors(); self.drawStill(); });
    this.themeObs.observe(document.body, { attributes: true, attributeFilter: ["data-md-color-scheme"] });

    this.canvas.addEventListener("click", function () { self.newEvent(); }, { signal: signal });
    this.canvas.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); self.newEvent(); }
    }, { signal: signal });
    reduceMotion.addEventListener("change", function () { self.drawStill(); self.loop(); }, { signal: signal });

    this.loop();
  }

  EventDisplay.prototype.destroy = function () {
    this.alive = false;
    this.abort.abort();
    this.resizeObs.disconnect();
    this.visObs.disconnect();
    this.themeObs.disconnect();
    cancelAnimationFrame(this.raf);
  };

  EventDisplay.prototype.readColors = function () {
    var s = getComputedStyle(this.canvas), c = this.colors;
    ["ring", "cell", "track", "soft", "em", "had", "mu", "e", "met"].forEach(function (k) {
      c[k] = s.getPropertyValue("--evd-" + k).trim();
    });
  };

  EventDisplay.prototype.resize = function () {
    var w = this.canvas.getBoundingClientRect().width;
    if (!w) return;
    var dpr = Math.min(2, window.devicePixelRatio || 1);
    this.W = w; this.R = w / 2;
    this.canvas.width = Math.round(w * dpr);
    this.canvas.height = Math.round(w * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (this.ev) this.buildPaths(this.ev);
    this.drawStill();
  };

  EventDisplay.prototype.makeEvent = function () {
    var ev = {
      tracks: [],
      em: new Float32Array(N_EM),
      had: new Float32Array(N_HAD),
      t0: performance.now()
    };
    var visX = 0, visY = 0;

    function deposit(arr, phi, E, spread) {
      var n = arr.length, c = wrapAngle(phi) / TAU * n;
      for (var k = -3; k <= 3; k++) {
        var i = Math.floor(c + k);
        var w = Math.exp(-Math.pow(i + 0.5 - c, 2) / (2 * spread * spread));
        arr[((i % n) + n) % n] += E * w;
      }
    }
    function addVisible(phi, E) { visX += E * Math.cos(phi); visY += E * Math.sin(phi); }
    function charge() { return Math.random() < 0.5 ? -1 : 1; }

    // Two b-jets, loosely back to back
    var j1 = rnd(0, TAU), j2 = j1 + Math.PI + rnd(-1.3, 1.3);
    [j1, j2].forEach(function (phi) {
      var E = rnd(45, 150), n = 4 + Math.floor(rnd(0, 5));
      for (var i = 0; i < n; i++) {
        ev.tracks.push({ phi: phi + gauss() * 0.13, pt: rnd(2, E / 3), q: charge(), kind: "jet", rmax: L.trkOut });
      }
      deposit(ev.had, phi, E * 0.7, 1.1);
      deposit(ev.em, phi, E * 0.3, 1.4);
      addVisible(phi, E);
    });

    // One electron and one muon, isolated from the jets and each other
    var pe, pm;
    do { pe = rnd(0, TAU); } while (angleBetween(pe, j1) < 0.7 || angleBetween(pe, j2) < 0.7);
    do { pm = rnd(0, TAU); } while (angleBetween(pm, j1) < 0.6 || angleBetween(pm, j2) < 0.6 || angleBetween(pm, pe) < 0.6);
    var qe = charge(), ptE = rnd(25, 90), ptM = rnd(20, 80);
    ev.tracks.push({ phi: pe, pt: ptE, q: qe, kind: "e", rmax: L.emIn + 0.03 });
    deposit(ev.em, pe, ptE * 1.2, 0.6);
    addVisible(pe, ptE);
    ev.tracks.push({ phi: pm, pt: ptM, q: -qe, kind: "mu", rmax: L.muOut });
    addVisible(pm, ptM);

    // Soft underlying-event / pile-up tracks
    var nSoft = 12 + Math.floor(rnd(0, 12));
    for (var i = 0; i < nSoft; i++) {
      ev.tracks.push({ phi: rnd(0, TAU), pt: rnd(0.35, 3), q: charge(), kind: "soft", rmax: L.trkOut });
    }

    // Missing transverse momentum balances the visible objects (+ resolution smearing)
    var mx = -visX + gauss() * 15, my = -visY + gauss() * 15;
    ev.met = { phi: Math.atan2(my, mx), E: Math.hypot(mx, my) };
    ev.info = {
      e: (qe > 0 ? "e⁺ " : "e⁻ ") + Math.round(ptE),
      mu: (qe > 0 ? "μ⁻ " : "μ⁺ ") + Math.round(ptM),
      met: Math.round(ev.met.E)
    };
    this.buildPaths(ev);
    return ev;
  };

  // Charged tracks are circles through the origin: radius ∝ pT, sense set by charge.
  EventDisplay.prototype.buildPaths = function (ev) {
    var R = this.R;
    ev.muChamber = -1;
    ev.tracks.forEach(function (t) {
      var rho = t.pt * 0.12 * R, k = t.q / rho, step = Math.max(1, R * 0.008);
      var sMax = Math.min(2 * R, Math.PI * rho * 1.6), pts = [];
      for (var s = 0; s <= sMax; s += step) {
        var x = (Math.sin(t.phi + k * s) - Math.sin(t.phi)) / k;
        var y = (-Math.cos(t.phi + k * s) + Math.cos(t.phi)) / k;
        if (Math.hypot(x, y) > t.rmax * R) break;
        pts.push(x, y);
      }
      t.pts = pts;
      if (t.kind === "mu" && pts.length > 2) {
        var n = pts.length;
        ev.muChamber = Math.floor(wrapAngle(Math.atan2(pts[n - 1], pts[n - 2])) / TAU * N_MU);
      }
    });
  };

  EventDisplay.prototype.annulus = function (r0, r1, a0, a1, fill) {
    var ctx = this.ctx;
    ctx.beginPath();
    ctx.arc(0, 0, r1, a0, a1);
    ctx.arc(0, 0, r0, a1, a0, true);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
  };

  EventDisplay.prototype.drawDetector = function () {
    var ctx = this.ctx, R = this.R, c = this.colors, i, a;
    ctx.globalAlpha = 1;
    this.annulus(L.emIn * R, L.emOut * R, 0, TAU, c.cell);
    this.annulus(L.hadIn * R, L.hadOut * R, 0, TAU, c.cell);
    ctx.strokeStyle = c.ring;
    ctx.lineWidth = 1;
    for (i = 0; i < 4; i++) {
      var r = (L.trkIn + (i + 1) * (L.trkOut - L.trkIn) / 4.4) * R;
      ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke();
    }
    ctx.globalAlpha = 0.55;
    function spokes(n, r0, r1) {
      for (i = 0; i < n; i++) {
        a = i / n * TAU;
        ctx.beginPath();
        ctx.moveTo(Math.cos(a) * r0, Math.sin(a) * r0);
        ctx.lineTo(Math.cos(a) * r1, Math.sin(a) * r1);
        ctx.stroke();
      }
    }
    spokes(N_EM, L.emIn * R, L.emOut * R);
    spokes(N_HAD, L.hadIn * R, L.hadOut * R);
    ctx.globalAlpha = 1;
    for (i = 0; i < N_MU; i++) {
      var a0 = i / N_MU * TAU + MU_GAP, a1 = (i + 1) / N_MU * TAU - MU_GAP;
      this.annulus(L.muIn * R, L.muOut * R, a0, a1, c.cell);
      ctx.stroke();
    }
  };

  EventDisplay.prototype.draw = function (now) {
    if (!this.W) return;
    var ctx = this.ctx, R = this.R, c = this.colors, ev = this.ev, i;
    ctx.clearRect(0, 0, this.W, this.W);
    ctx.save();
    ctx.translate(R, R);
    this.drawDetector();

    if (ev) {
      var T = reduceMotion.matches ? T_HOLD : now - ev.t0;
      var grow = easeOut(clamp(T / T_GROW));
      var cellA = clamp((T - T_CELLS) / 500);
      var fade = T > T_HOLD ? 1 - clamp((T - T_HOLD) / T_FADE) : 1;

      // Calorimeter and muon-chamber hits
      for (i = 0; i < N_EM; i++) if (ev.em[i] > 1) {
        ctx.globalAlpha = Math.min(1, ev.em[i] / 40) * cellA * fade;
        this.annulus(L.emIn * R + 1, L.emOut * R - 1, i / N_EM * TAU + 0.005, (i + 1) / N_EM * TAU - 0.005, c.em);
      }
      for (i = 0; i < N_HAD; i++) if (ev.had[i] > 1) {
        ctx.globalAlpha = Math.min(1, ev.had[i] / 50) * cellA * fade;
        this.annulus(L.hadIn * R + 1, L.hadOut * R - 1, i / N_HAD * TAU + 0.008, (i + 1) / N_HAD * TAU - 0.008, c.had);
      }
      if (ev.muChamber >= 0) {
        ctx.globalAlpha = cellA * fade;
        this.annulus(L.muIn * R + 1, L.muOut * R - 1, ev.muChamber / N_MU * TAU + MU_GAP, (ev.muChamber + 1) / N_MU * TAU - MU_GAP, c.mu);
      }

      // Tracks
      ctx.lineCap = "round";
      ev.tracks.forEach(function (t) {
        var n = Math.floor(t.pts.length / 2 * grow);
        if (n < 2) return;
        ctx.globalAlpha = fade * (t.kind === "soft" ? 0.55 : 1);
        ctx.strokeStyle = t.kind === "e" ? c.e : t.kind === "mu" ? c.mu : t.kind === "soft" ? c.soft : c.track;
        ctx.lineWidth = t.kind === "soft" ? 1 : t.kind === "jet" ? 1.4 : 2.2;
        ctx.beginPath();
        ctx.moveTo(t.pts[0], t.pts[1]);
        for (var j = 1; j < n; j++) ctx.lineTo(t.pts[2 * j], t.pts[2 * j + 1]);
        ctx.stroke();
      });

      // Missing transverse momentum: dashed arrow
      var phi = ev.met.phi, cs = Math.cos(phi), sn = Math.sin(phi);
      var r0 = L.trkIn * R, len = r0 + Math.min(0.42, ev.met.E / 220) * R * grow;
      ctx.globalAlpha = fade * cellA;
      ctx.strokeStyle = c.met;
      ctx.fillStyle = c.met;
      ctx.lineWidth = 1.6;
      ctx.setLineDash([5, 4]);
      ctx.beginPath(); ctx.moveTo(cs * r0, sn * r0); ctx.lineTo(cs * len, sn * len); ctx.stroke();
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(cs * len, sn * len);
      ctx.lineTo(cs * len - 8 * Math.cos(phi - 0.4), sn * len - 8 * Math.sin(phi - 0.4));
      ctx.lineTo(cs * len - 8 * Math.cos(phi + 0.4), sn * len - 8 * Math.sin(phi + 0.4));
      ctx.closePath();
      ctx.fill();

      if (!reduceMotion.matches && T > T_HOLD + T_FADE) this.newEvent();
    }
    ctx.restore();
    ctx.globalAlpha = 1;
  };

  EventDisplay.prototype.drawStill = function () {
    if (reduceMotion.matches) this.draw(performance.now());
  };

  EventDisplay.prototype.newEvent = function () {
    this.ev = this.makeEvent();
    if (this.caption) {
      var i = this.ev.info;
      this.caption.innerHTML =
        'Simulated t<span class="hp-ob">t</span> → bℓν bℓν collision' +
        '<br><span class="hp-evd-cap-info">' + i.e + " GeV · " + i.mu + " GeV · 2 b-jets · " +
        "E<sub>T</sub><sup>miss</sup> " + i.met + " GeV</span>";
    }
    this.drawStill();
  };

  EventDisplay.prototype.loop = function () {
    var self = this;
    cancelAnimationFrame(this.raf);
    if (reduceMotion.matches) return;
    function frame(now) {
      if (!self.alive) return;
      if (self.visible && !document.hidden) self.draw(now);
      self.raf = requestAnimationFrame(frame);
    }
    this.raf = requestAnimationFrame(frame);
  };

  /* ================================================================
     2. CAREER TIMELINE
     ================================================================ */

  function Timeline(tl) {
    this.tl = tl;
    this.fill = tl.querySelector(".hp-tl-fill");
    this.abort = new AbortController();
    var self = this, signal = this.abort.signal, pending = false;
    tl.classList.add("hp-tl--live");

    function schedule() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () { pending = false; self.update(); });
    }
    window.addEventListener("scroll", schedule, { passive: true, signal: signal });
    window.addEventListener("resize", schedule, { signal: signal });
    tl.querySelectorAll("details").forEach(function (d) {
      d.addEventListener("toggle", schedule, { signal: signal });
    });
    reduceMotion.addEventListener("change", schedule, { signal: signal });
    this.update();
  }

  Timeline.prototype.update = function () {
    var r = this.tl.getBoundingClientRect();
    // The line reaches the item that is 65% of the way down the viewport
    var p = reduceMotion.matches ? 1 : clamp((window.innerHeight * 0.65 - r.top) / r.height);
    if (this.fill) this.fill.style.setProperty("--p", p.toFixed(4));
    var cut = r.top + p * r.height;
    this.tl.querySelectorAll(".hp-tl-item").forEach(function (el) {
      var top = el.getBoundingClientRect().top;
      el.classList.toggle("reached", el.offsetParent !== null && top + 8 <= cut);
    });
  };

  Timeline.prototype.destroy = function () { this.abort.abort(); };

  /* ================================================================
     INIT (runs on every instant-navigation page load)
     ================================================================ */

  /* ---------- Hero subtitle: no "·" at the start of a wrapped line ---------- */
  function SubLine(el) {
    // Items: role, then affiliations. If the line has to wrap, break after the
    // role first ("Particle physicist" / "TU Dresden · ATLAS Experiment"), then
    // wherever else it still wraps. A wrapped item loses its leading "·".
    var items = el.querySelectorAll(".hp-sub-item");
    function top(i) {
      return (items[i].querySelector("a") || items[i]).getBoundingClientRect().top;
    }
    function mark() {
      items.forEach(function (it) { it.classList.remove("hp-line-start"); });
      if (items.length < 2 || top(items.length - 1) <= top(0) + 2) return;  // fits on one line
      items[1].classList.add("hp-line-start");
      for (var i = 2; i < items.length; i++) {
        if (top(i) > top(i - 1) + 2) items[i].classList.add("hp-line-start");
      }
    }
    // Line breaks move when the width changes or the web font arrives.
    this.mark = mark;
    this.ro = typeof ResizeObserver !== "undefined" ? new ResizeObserver(mark) : null;
    if (this.ro) this.ro.observe(el);
    if (document.fonts) {
      document.fonts.addEventListener("loadingdone", mark);
      document.fonts.ready.then(mark);
    }
    window.addEventListener("load", mark);
    mark();
  }
  SubLine.prototype.destroy = function () {
    if (this.ro) this.ro.disconnect();
    if (document.fonts) document.fonts.removeEventListener("loadingdone", this.mark);
    window.removeEventListener("load", this.mark);
  };

  /* ---------- Research cards: rise in, staggered, on first view ---------- */
  // Each card's topic animation (data/card-anims/*.svg) plays once after the
  // card rises in, then loops while the card is hovered (after HOVER_DELAY_MS)
  // or focused. A loop is
  // always allowed to finish, so it stops on its final frame (= resting state).
  var ANIM_MS = 5000;
  // The pointer must rest on a card this long before it plays, so cards
  // crossed on the way to another one don't all start.
  var HOVER_DELAY_MS = 1000;

  function Reveal(grid) {
    var self = this;
    var cards = grid.querySelectorAll(".hp-rc");
    this.timers = [];
    this.abort = new AbortController();
    this.io = null;
    if (!("IntersectionObserver" in window) || reduceMotion.matches || !cards.length) return;

    cards.forEach(function (c, i) {
      c.style.setProperty("--i", i);
      c.style.setProperty("--anim-dur", ANIM_MS + "ms");
      if (!c.querySelector(".hp-anim")) return;
      var hoverTimer = null;
      c.addEventListener("mouseenter", function () {
        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(function () { self.play(c); }, HOVER_DELAY_MS);
        self.timers.push(hoverTimer);
      }, { signal: self.abort.signal });
      c.addEventListener("mouseleave", function () { clearTimeout(hoverTimer); }, { signal: self.abort.signal });
      // Keyboard focus is deliberate: play straight away
      c.addEventListener("focusin", function () { self.play(c); }, { signal: self.abort.signal });
    });
    grid.classList.add("hp-reveal");
    this.io = new IntersectionObserver(function (entries, io) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        // Whole grid at once, so the stagger reads left-to-right, top-to-bottom
        cards.forEach(function (c, i) {
          c.classList.add("in");
          if (c.querySelector(".hp-anim")) self.later(function () { self.play(c); }, 450 + i * 350);
        });
        io.disconnect();
      });
    }, { threshold: 0.2 });
    this.io.observe(grid);
  }
  Reveal.prototype.later = function (fn, ms) { this.timers.push(setTimeout(fn, ms)); };
  Reveal.prototype.play = function (card) {
    if (card.classList.contains("hp-anim-run")) return;   // already playing
    var self = this;
    card.classList.add("hp-anim-run");
    function loopEnd() {
      // Just before the loop ends (all animations hold their final frame by then)
      if (card.matches(":hover") || card.matches(":focus-within")) self.later(loopEnd, ANIM_MS);
      else card.classList.remove("hp-anim-run");
    }
    this.later(loopEnd, ANIM_MS - 40);
  };
  Reveal.prototype.destroy = function () {
    if (this.io) this.io.disconnect();
    this.abort.abort();
    this.timers.forEach(clearTimeout);
  };

  var instances = [];

  function init() {
    instances.forEach(function (x) { x.destroy(); });
    instances = [];
    document.querySelectorAll(".hp-evd").forEach(function (box) {
      if (box.querySelector("canvas")) instances.push(new EventDisplay(box));
    });
    document.querySelectorAll(".hp-tl").forEach(function (tl) {
      instances.push(new Timeline(tl));
    });
    document.querySelectorAll(".hp-rg").forEach(function (grid) {
      instances.push(new Reveal(grid));
    });
    document.querySelectorAll(".hp-sub").forEach(function (el) {
      instances.push(new SubLine(el));
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
