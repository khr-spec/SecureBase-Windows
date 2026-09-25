'use strict';
(() => {
  document.documentElement.classList.add('js-ready');
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-navigation');
  if (toggle && nav) {
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
      }
    });
  }

  // Original image links remain usable when JavaScript is unavailable.
  const dialog = document.querySelector('#image-dialog');
  const image = document.querySelector('#lightbox-image');
  const title = document.querySelector('#lightbox-title');
  const original = document.querySelector('#lightbox-original');
  const zoom = document.querySelector('.lightbox-zoom');
  let lastFocus = null;
  if (dialog && typeof dialog.showModal === 'function') {
    document.addEventListener('click', event => {
      const link = event.target.closest('a[data-lightbox]');
      if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      lastFocus = link;
      image.src = link.href;
      image.alt = link.dataset.caption || link.querySelector('img')?.alt || 'Billedbevis';
      title.textContent = image.alt;
      original.href = link.href;
      dialog.classList.remove('is-zoomed');
      zoom.setAttribute('aria-pressed', 'false');
      zoom.textContent = 'Zoom';
      dialog.showModal();
      document.body.style.overflow = 'hidden';
    });
    dialog.querySelector('.lightbox-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener('close', () => {
      document.body.style.overflow = '';
      image.removeAttribute('src');
      if (lastFocus?.isConnected) lastFocus.focus();
    });
    zoom.addEventListener('click', () => {
      const enabled = dialog.classList.toggle('is-zoomed');
      zoom.setAttribute('aria-pressed', String(enabled));
      zoom.textContent = enabled ? 'Tilpas' : 'Zoom';
    });
  }

  const toast = document.querySelector('.toast');
  let toastTimer;
  function notify(message) {
    if (!toast) return;
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('is-visible');
    toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 3500);
  }
  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(text); return true; } catch (_) { /* local preview fallback */ }
    }
    const box = document.createElement('textarea');
    box.value = text;
    box.style.position = 'fixed'; box.style.opacity = '0';
    document.body.append(box); box.select();
    let ok = false;
    try { ok = document.execCommand('copy'); } catch (_) { ok = false; }
    box.remove(); return ok;
  }
  document.querySelectorAll('.copy-code').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const code = button.closest('.code-block').querySelector('pre');
      const ok = await copyText(code.textContent);
      button.focus();
      notify(ok ? 'Koden er kopieret.' : 'Kopiér manuelt: markér teksten i kodefeltet.');
    });
  });

  // Everything is in the HTML: filters work offline without fetch or a backend.
  const cards = Array.from(document.querySelectorAll('.evidence-card'));
  if (cards.length) {
    const controls = document.querySelector('.gallery-tools');
    const buttons = Array.from(document.querySelectorAll('[data-filter]'));
    const search = document.querySelector('#evidence-search');
    const count = document.querySelector('#gallery-count');
    const empty = document.querySelector('.empty-state');
    const requested = new URLSearchParams(location.search).get('modul');
    let module = buttons.some(b => b.dataset.filter === requested) ? requested : 'all';
    controls.hidden = false;
    function apply(updateURL) {
      const q = search.value.toLocaleLowerCase('da').trim();
      let visible = 0;
      cards.forEach(card => {
        const match = (module === 'all' || card.dataset.module === module) && (!q || card.dataset.search.toLocaleLowerCase('da').includes(q));
        card.hidden = !match; if (match) visible++;
      });
      buttons.forEach(button => {
        const active = button.dataset.filter === module;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
      });
      count.textContent = `${visible} af ${cards.length} billeder`;
      empty.hidden = visible !== 0;
      if (updateURL) {
        const url = new URL(location.href);
        if (module === 'all') url.searchParams.delete('modul'); else url.searchParams.set('modul', module);
        try { history.replaceState(null, '', url); } catch (_) { /* file:// previews can still filter */ }
      }
    }
    buttons.forEach(button => button.addEventListener('click', () => { module = button.dataset.filter; apply(true); }));
    search.addEventListener('input', () => apply(false));
    apply(false);
  }

  // Highlight the current section in the desktop contents list.
  const tocLinks = Array.from(document.querySelectorAll('.toc-sidebar a'));
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const lookup = new Map(tocLinks.map(link => [decodeURIComponent(link.hash.slice(1)), link]));
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        tocLinks.forEach(link => link.classList.remove('is-current'));
        lookup.get(entry.target.id)?.classList.add('is-current');
      }
    }, { rootMargin: '-100px 0px -60% 0px', threshold: 0 });
    document.querySelectorAll('.prose h2').forEach(h => observer.observe(h));
  }
})();
