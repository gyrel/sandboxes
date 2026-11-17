(function () {
  function openSearch() {
    var toggle = document.getElementById('__search');
    var input = document.querySelector('.md-search__input');
    if (toggle && !toggle.checked) toggle.click();
    if (input) window.setTimeout(function () { input.focus(); }, 0);
  }
  function initSearch() {
    document.querySelectorAll('[data-shortcut-mod]').forEach(function (key) {
      key.textContent = /Mac|iPhone|iPad/.test(navigator.platform) ? '⌘' : 'Ctrl';
    });
    document.querySelectorAll('[data-open-search]').forEach(function (button) {
      if (button.dataset.searchReady) return;
      button.dataset.searchReady = 'true';
      button.addEventListener('click', openSearch);
    });
  }
  document.addEventListener('keydown', function (event) {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      openSearch();
    }
  });
  if (typeof document$ !== 'undefined') document$.subscribe(initSearch);
  else document.addEventListener('DOMContentLoaded', initSearch);
}());
