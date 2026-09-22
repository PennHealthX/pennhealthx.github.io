/**
 * Opens a specific project section based on URL hash.
 * Usage: /projects#podcast, /projects#sdoh-accelerator, etc.
 */
(function() {
  function openSectionFromHash() {
    const hash = window.location.hash.slice(1);
    if (!hash) return;

    const detail = document.getElementById(hash);
    if (detail && detail.tagName === 'DETAILS') {
      detail.open = true;
      setTimeout(() => detail.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', openSectionFromHash);
  } else {
    openSectionFromHash();
  }

  window.addEventListener('hashchange', openSectionFromHash);
})();
