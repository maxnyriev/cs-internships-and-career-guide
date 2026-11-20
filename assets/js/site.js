/* Small progressive enhancements. Every page works without this file. */
(function () {
  'use strict';

  /* ---------- 1. Job list filter (pages with a job table) ---------- */
  function setupFilter() {
    var main = document.getElementById('main');
    if (!main || !main.classList.contains('wide')) return;
    var tables = Array.prototype.slice.call(main.querySelectorAll('table')).filter(function (t) {
      var head = t.querySelector('thead');
      return head && /company/i.test(head.textContent) && /role/i.test(head.textContent);
    });
    if (!tables.length) return;

    // Rows are indexed on first use, not at page load, so long lists stay fast to open.
    var rows = null, total = 0;
    tables.forEach(function (t) { total += t.querySelectorAll('tbody tr').length; });
    function index() {
      if (rows) return;
      rows = [];
      tables.forEach(function (t) {
      var heads = Array.prototype.map.call(t.querySelectorAll('thead th'), function (th) { return th.textContent.trim().toLowerCase(); });
      var tagCol = heads.indexOf('tags');
      Array.prototype.forEach.call(t.querySelectorAll('tbody tr'), function (tr) {
        var cells = tr.children;
        var tags = tagCol >= 0 && cells[tagCol] ? cells[tagCol].textContent.toLowerCase() : '';
        var text = '';
        for (var i = 0; i < cells.length; i++) if (i !== tagCol) text += ' ' + cells[i].textContent;
        rows.push({ el: tr, text: text.toLowerCase(), tags: tags, show: true });
      });
      });
    }

    var bar = document.createElement('form');
    bar.className = 'filter-bar';
    bar.setAttribute('role', 'search');
    bar.setAttribute('aria-label', 'Filter jobs');
    bar.innerHTML =
      '<div class="filter-field">' +
        '<label for="job-q">Filter jobs</label>' +
        '<input id="job-q" type="search" autocomplete="off" spellcheck="false" placeholder="Company, role or city (e.g. Texas, embedded, Google)">' +
      '</div>' +
      '<div class="filter-toggles">' +
        '<label class="toggle"><input type="checkbox" id="job-open"> Hide citizens-only, clearance, ITAR and gov roles</label>' +
        '<label class="toggle"><input type="checkbox" id="job-remote"> Remote only</label>' +
        '<label class="toggle"><input type="checkbox" id="job-term"> Co-op, fall, spring or part-time only</label>' +
      '</div>' +
      '<p class="filter-status" id="job-count" role="status" aria-live="polite"></p>';
    var slot = document.getElementById('job-filter');
    if (slot) slot.appendChild(bar); else tables[0].parentNode.insertBefore(bar, tables[0]);

    var q = bar.querySelector('#job-q'), open = bar.querySelector('#job-open'),
        remote = bar.querySelector('#job-remote'), term = bar.querySelector('#job-term'),
        count = bar.querySelector('#job-count');

    // Restore from the URL so a filtered list can be shared (?q=texas&remote=1).
    var params = new URLSearchParams(location.search);
    q.value = params.get('q') || '';
    open.checked = params.get('open') === '1';
    remote.checked = params.get('remote') === '1';
    term.checked = params.get('term') === '1';

    var RESTRICTED = /citizens|clearance|secret|ts\/sci|public trust|itar|\bgov\b/;
    var TERMS = /co-op|fall|spring|part-time/;
    var timer = null;

    /* Cross-page search: lazy-load the full index on first keystroke */
    var allJobs = null, loadingIndex = false;
    var crossBox = document.createElement('div');
    crossBox.className = 'cross-page-results';
    crossBox.hidden = true;
    bar.parentNode.insertBefore(crossBox, bar.nextSibling);
    function loadIndex(cb) {
      if (allJobs) return cb();
      if (loadingIndex) return;
      loadingIndex = true;
      var base = document.querySelector('link[rel="canonical"]');
      var root = base ? base.href.replace(/[^/]*$/, '') : location.href.replace(/[^/]*$/, '');
      fetch(root + 'assets/search-index.json').then(function (r) { return r.json(); }).then(function (data) {
        allJobs = data; cb();
      }).catch(function () { loadingIndex = false; });
    }
    var currentPageFile = location.pathname.split('/').pop() || 'index.html';
    if (currentPageFile.indexOf('.') === -1) currentPageFile += '.html';

    function matchesFilter(text, words) {
      for (var w = 0; w < words.length; w++) {
        var variants = expandWord(words[w]);
        var found = false;
        for (var v = 0; !found && v < variants.length; v++) {
          if (text.indexOf(variants[v]) !== -1) found = true;
        }
        if (!found) return false;
      }
      return true;
    }

    function searchCrossPage(words, openOnly, remoteOnly, termOnly) {
      if (!allJobs || !words.length && !openOnly && !remoteOnly && !termOnly) {
        crossBox.hidden = true; return;
      }
      // Index entries: [company, title, location, tags, url, page_file]
      var pageCounts = {};  // page_file → count
      var totalOther = 0;
      for (var i = 0; i < allJobs.length; i++) {
        var j = allJobs[i];
        if (j[5] === currentPageFile) continue;  // skip current page
        var text = (j[0] + ' ' + j[1] + ' ' + j[2] + ' ' + j[3]).toLowerCase();
        if (words.length && !matchesFilter(text, words)) continue;
        if (openOnly && RESTRICTED.test(j[3].toLowerCase())) continue;
        if (remoteOnly && text.indexOf('remote') === -1) continue;
        if (termOnly && !TERMS.test(j[3].toLowerCase())) continue;
        pageCounts[j[5]] = (pageCounts[j[5]] || 0) + 1;
        totalOther++;
      }
      if (totalOther === 0) { crossBox.hidden = true; return; }
      // Build links grouped by section
      var base = location.pathname.replace(/[^/]*$/, '');
      var html = '<strong>' + totalOther + ' more match' + (totalOther > 1 ? 'es' : '') + ' on other pages:</strong> ';
      var links = [];
      var pages = Object.keys(pageCounts).sort();
      for (var p = 0; p < pages.length; p++) {
        var pf = pages[p];
        var label = pf.replace('.html', '').replace(/-(\d+)$/, ' p$1');
        links.push('<a href="' + base + pf + location.search + '">' + label + ' (' + pageCounts[pf] + ')</a>');
      }
      html += links.join(', ');
      crossBox.innerHTML = html;
      crossBox.hidden = false;
    }

    /* State name ↔ abbreviation aliases so "texas" finds "TX" and vice versa. */
    var STATE_ALIASES = {
      'alabama':'al','alaska':'ak','arizona':'az','arkansas':'ar','california':'ca',
      'colorado':'co','connecticut':'ct','delaware':'de','florida':'fl','georgia':'ga',
      'hawaii':'hi','idaho':'id','illinois':'il','indiana':'in','iowa':'ia',
      'kansas':'ks','kentucky':'ky','louisiana':'la','maine':'me','maryland':'md',
      'massachusetts':'ma','michigan':'mi','minnesota':'mn','mississippi':'ms',
      'missouri':'mo','montana':'mt','nebraska':'ne','nevada':'nv','new hampshire':'nh',
      'new jersey':'nj','new mexico':'nm','new york':'ny','north carolina':'nc',
      'north dakota':'nd','ohio':'oh','oklahoma':'ok','oregon':'or','pennsylvania':'pa',
      'rhode island':'ri','south carolina':'sc','south dakota':'sd','tennessee':'tn',
      'texas':'tx','utah':'ut','vermont':'vt','virginia':'va','washington':'wa',
      'west virginia':'wv','wisconsin':'wi','wyoming':'wy',
      'district of columbia':'dc','d.c.':'dc'
    };
    var ABBREV_TO_STATE = {};
    Object.keys(STATE_ALIASES).forEach(function (name) { ABBREV_TO_STATE[STATE_ALIASES[name]] = name; });

    var CITY_ALIASES = {
      'nyc':'new york','sf':'san francisco','la':'los angeles','dc':'washington',
      'philly':'philadelphia','atl':'atlanta','chi':'chicago','dfw':'dallas',
      'stl':'st. louis','slc':'salt lake city'
    };

    function expandWord(w) {
      var out = [w];
      if (STATE_ALIASES[w]) out.push(STATE_ALIASES[w]);
      if (ABBREV_TO_STATE[w]) out.push(ABBREV_TO_STATE[w]);
      if (CITY_ALIASES[w]) out.push(CITY_ALIASES[w]);
      return out;
    }

    function apply() {
      index();
      var words = q.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      var shown = 0;
      // Decide every row first, then write once per row (no layout reads in between).
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i], ok = true;
        for (var w = 0; ok && w < words.length; w++) {
          var variants = expandWord(words[w]);
          var found = false;
          for (var v = 0; !found && v < variants.length; v++) {
            if (r.text.indexOf(variants[v]) !== -1 || r.tags.indexOf(variants[v]) !== -1) found = true;
          }
          if (!found) ok = false;
        }
        if (ok && open.checked && RESTRICTED.test(r.tags)) ok = false;
        if (ok && remote.checked && r.tags.indexOf('remote') === -1 && r.text.indexOf('remote') === -1) ok = false;
        if (ok && term.checked && !TERMS.test(r.tags)) ok = false;
        r.next = ok;
        if (ok) shown++;
      }
      // Write only rows whose visibility changed (one batch of writes, no reads).
      for (var j = 0; j < rows.length; j++) {
        if (rows[j].next !== rows[j].show) { rows[j].show = rows[j].next; rows[j].el.hidden = !rows[j].show; }
      }
      var filtered = words.length || open.checked || remote.checked || term.checked;
      count.textContent = filtered ? 'Showing ' + shown + ' of ' + total + ' jobs on this page' : total + ' jobs';

      // Cross-page results (only if index is loaded)
      if (filtered && allJobs) searchCrossPage(words, open.checked, remote.checked, term.checked);
      else crossBox.hidden = true;

      var p = new URLSearchParams();
      if (q.value.trim()) p.set('q', q.value.trim());
      if (open.checked) p.set('open', '1');
      if (remote.checked) p.set('remote', '1');
      if (term.checked) p.set('term', '1');
      var qs = p.toString();
      try { history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash); } catch (e) { /* file:// or sandboxed */ }
    }
    function later() { clearTimeout(timer); timer = setTimeout(apply, 150); }

    q.addEventListener('input', function () {
      loadIndex(function () {
        // Re-run cross-page after index arrives
        var words = q.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
        if (words.length || open.checked || remote.checked || term.checked) {
          searchCrossPage(words, open.checked, remote.checked, term.checked);
        }
      });
      later();
    });
    [open, remote, term].forEach(function (c) {
      c.addEventListener('change', function () {
        loadIndex(function () {
          var words = q.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
          searchCrossPage(words, open.checked, remote.checked, term.checked);
        });
        apply();
      });
    });
    bar.addEventListener('submit', function (e) { e.preventDefault(); apply(); });
    q.addEventListener('keydown', function (e) { if (e.key === 'Escape' && q.value) { q.value = ''; apply(); } });
    // Only filter at load when the URL asks for it; otherwise just show the count.
    if (q.value || open.checked || remote.checked || term.checked) {
      apply();
      loadIndex(function () {
        var words = q.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
        searchCrossPage(words, open.checked, remote.checked, term.checked);
      });
    }
    else count.textContent = total + ' jobs';
    q.addEventListener('focus', function () {
      if ('requestIdleCallback' in window) requestIdleCallback(index); else setTimeout(index, 0);
      loadIndex(function () {}); // pre-fetch index on focus
    }, { once: true });
  }

  /* ---------- 2. Copy buttons on message templates in the guides ---------- */
  function setupCopy() {
    if (!navigator.clipboard || location.pathname.indexOf('/guides/') === -1) return;
    var quotes = document.querySelectorAll('#main blockquote');
    Array.prototype.forEach.call(quotes, function (bq) {
      var text = bq.innerText.trim();
      if (text.length < 60 || !/\[[^\]]+\]/.test(text)) return; // only fill-in-the-blank templates
      var wrap = document.createElement('div');
      wrap.className = 'copy-row';
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'copy-btn';
      btn.textContent = 'Copy template';
      var status = document.createElement('span');
      status.className = 'copy-status';
      status.setAttribute('role', 'status');
      btn.addEventListener('click', function () {
        navigator.clipboard.writeText(text).then(function () {
          status.textContent = 'Copied. Replace the [brackets] before you send it.';
        }, function () {
          status.textContent = 'Copy failed. Select the text and copy it instead.';
        });
      });
      wrap.appendChild(btn);
      wrap.appendChild(status);
      bq.parentNode.insertBefore(wrap, bq.nextSibling);
    });
  }

  /* ---------- 3. Wide guide tables: reachable by keyboard when they scroll sideways ---------- */
  function setupScrollTables() {
    if (location.pathname.indexOf('/guides/') === -1) return; // job tables have links, so they're already reachable
    var tables = document.querySelectorAll('#main table');
    // Read all widths first, then write (no interleaved layout reads and writes).
    var wide = Array.prototype.filter.call(tables, function (t) { return t.scrollWidth > t.clientWidth + 1; });
    wide.forEach(function (t) {
      if (t.querySelector('a, button, input')) return;
      var h = t.previousElementSibling;
      while (h && !/^H[2-4]$/.test(h.tagName)) h = h.previousElementSibling;
      t.setAttribute('tabindex', '0');
      t.setAttribute('role', 'region');
      t.setAttribute('aria-label', (h ? h.textContent.trim() + ' ' : '') + 'table (scrolls sideways)');
    });
  }

  /* ---------- 4. Back-to-top button on long pages ---------- */
  function setupBackToTop() {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'back-to-top';
    btn.setAttribute('aria-label', 'Back to top');
    btn.textContent = '↑ Top';
    btn.hidden = true;
    document.body.appendChild(btn);
    var visible = false;
    function toggle() {
      var show = window.scrollY > 600;
      if (show !== visible) { visible = show; btn.hidden = !show; }
    }
    window.addEventListener('scroll', toggle, { passive: true });
    btn.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  function init() { setupFilter(); setupCopy(); setupScrollTables(); setupBackToTop(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
