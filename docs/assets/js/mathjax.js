window.MathJax = {
  tex: {
    inlineMath: [["$", "$"], ["\\(", "\\)"]],
    displayMath: [["$$", "$$"], ["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex|pub-title|talk-title|hp-rc|md-content|md-typeset"
  },
  startup: {
    ready: function() {
      MathJax.startup.defaultReady();
    }
  }
};

document$.subscribe(() => {
  MathJax.startup.output.clearCache()
  MathJax.typesetClear()
  MathJax.texReset()
  MathJax.typesetPromise()
})

// Make site name in header clickable → links to home
document.addEventListener('DOMContentLoaded', function() {
  var topic = document.querySelector('.md-header__topic > .md-ellipsis');
  if (topic && !topic.closest('a')) {
    topic.style.cursor = 'pointer';
    topic.addEventListener('click', function() {
      window.location.href = document.querySelector('.md-header__button.md-logo').getAttribute('href');
    });
  }
});

// Also handle instant loading
if (typeof document$ !== 'undefined') {
  document$.subscribe(function() {
    var topic = document.querySelector('.md-header__topic > .md-ellipsis');
    if (topic && !topic.closest('a')) {
      topic.style.cursor = 'pointer';
      topic.onclick = function() {
        window.location.href = document.querySelector('.md-header__button.md-logo').getAttribute('href');
      };
    }

    // Blog sidebar: auto-expand Categories, hide Archive
    document.querySelectorAll('.md-nav__link').forEach(function(label) {
      var text = label.textContent.trim();
      if (text === 'Categories') {
        var toggleId = label.getAttribute('for');
        if (toggleId) {
          var checkbox = document.getElementById(toggleId);
          if (checkbox && !checkbox.checked) {
            checkbox.checked = true;
          }
        }
      }
      if (text === 'Archive') {
        var parent = label.closest('.md-nav__item');
        if (parent) {
          parent.style.display = 'none';
        }
      }
    });
  });
}
