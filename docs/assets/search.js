(function () {
  function openSearch() {
    var toggle = document.getElementById('__search');
    var input = document.querySelector('.md-search__input');
    if (toggle && !toggle.checked) toggle.click();
    if (input) window.setTimeout(function () { input.focus(); }, 0);
  }
  function initSearch() {
    var input = document.querySelector('.md-search__input');
    var output = document.querySelector('.md-search__output');
    if (input && output && !document.querySelector('.search-shortcuts')) {
      var russian = document.documentElement.lang === 'ru';
      var root = document.querySelector('.rheic-wordmark').href;
      var panel = document.createElement('div');
      panel.className = 'search-shortcuts';
      var heading = document.createElement('p');
      heading.textContent = russian ? 'Основные разделы' : 'Explore documentation';
      panel.appendChild(heading);
      var links = russian ? [['quickstart/', 'Начало работы'], ['cli/', 'Команды CLI'], ['runtime/', 'Нативный runtime'], ['comparison/', 'Сравнение с Docker'], ['limits/', 'Безопасность и ограничения']] : [['quickstart/', 'Get started'], ['cli/', 'CLI reference'], ['runtime/', 'Native runtime'], ['comparison/', 'Docker comparison'], ['limits/', 'Security and limits']];
      links.forEach(function (item) {
        var link = document.createElement('a');
        link.href = new URL(item[0], root).href;
        link.textContent = item[1];
        panel.appendChild(link);
      });
      output.before(panel);
      function update() { panel.hidden = input.value.trim().length > 0; output.classList.toggle('search-empty', !panel.hidden); }
      input.addEventListener('input', update);
      input.form.addEventListener('reset', function () { window.setTimeout(update, 0); });
      update();
    }
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
