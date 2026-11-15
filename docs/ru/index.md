---
title: Обзор
description: Установите выпущенную альфу Sandboxes от Rheic и запустите настоящие microVM на macOS ARM64. Быстрый старт, руководства, статус платформ, CLI и границы безопасности.
hide:
  - navigation
  - toc
  - path
  - footer
---

<!-- Wrapper only: the theme already renders the page's main landmark, so keep this a div. -->
<div class="rheic-home" markdown>

<section class="home-hero" aria-labelledby="home-title">
<div class="home-hero-copy" markdown>
<p class="home-eyebrow">Документация Rheic · Альфа Sandboxes выпущена · microVM на macOS ARM64</p>

<h1 id="home-title">Локальная граница для coding-агентов.</h1>

<p class="home-lede">Альфа Sandboxes выпущена. Rheic публикует CLI и daemon как релизные артефакты с контрольными суммами и SLSA-attestations, а daemon загружает настоящие microVM на macOS ARM64 через containerd, nerdbox shim и libkrun. Установите альфу, подключите агента к VM одной командой и посмотрите, что прошло live acceptance, а что пока не поддерживается.</p>

<div class="home-actions">
<a class="home-button" href="quickstart/">Начать с быстрого старта <span aria-hidden="true">↗</span></a>
<a class="home-button home-button-secondary" href="cli/">Открыть справочник CLI</a>
</div>

<label class="home-search-trigger" for="__search"><span>Поиск по документации</span><kbd>/</kbd></label>

<p class="home-footnote">Альфа-ПО · VM-путь проверен live на macOS ARM64 · Windows, облако и nested Docker не поддерживаются</p>
</div>

<div class="home-terminal" aria-label="Примеры локальных команд Rheic">
<div class="home-terminal-head"><span class="home-terminal-brand"><img src="../assets/rheic-shark.png" alt=""><strong>Запуск microVM</strong></span><span class="home-terminal-lang">rsbx</span></div>
<div class="home-terminal-code" markdown>
```sh
curl -fsSL https://raw.githubusercontent.com/rheic/sandboxes-cli/main/scripts/install.sh | sh
rsbx version

rsbx run shell .
rsbx ls

# Резервный режим: без --containerd VM не загружается
sandboxesd --state ~/.sandboxes \\
  --socket ~/.sandboxes/sandboxesd.sock
```
</div>
<div class="home-terminal-foot">Основной путь — microVM: <code>rsbx run</code> просит daemon загрузить VM. Режим state-only — резервный: он проверяет локальную control plane, не запускает VM и не подтверждает изоляцию.</div>
</div>
</section>

<section class="home-section" aria-labelledby="choose-title">
<div class="home-section-heading"><div><p class="home-kicker">Выберите точку входа</p><h2 id="choose-title">Что вы хотите сделать?</h2></div><p>Используйте руководство для своей задачи, затем проверьте требования и ограничения перед запуском команд.</p></div>
<div class="home-path-grid">
<a class="home-card" href="quickstart/"><span class="home-card-mark" aria-hidden="true">01</span><h3>Установить альфу и запустить microVM</h3><p>Установите выпущенные бинарники, запустите daemon с VM-backend и подключите shell к гостю.</p><span class="home-card-link">Быстрый старт →</span></a>
<a class="home-card" href="workspaces/"><span class="home-card-mark" aria-hidden="true">02</span><h3>Подготовить workspace агента</h3><p>Разберитесь с путями workspace, файловыми операциями и lifecycle sandbox.</p><span class="home-card-link">Руководство workspace →</span></a>
<a class="home-card" href="networking/"><span class="home-card-mark" aria-hidden="true">03</span><h3>Изучить сетевые границы</h3><p>Посмотрите deny-default модель, opt-in матрицы IPv6 и QUIC и опубликованные порты.</p><span class="home-card-link">Руководство по сети →</span></a>
<a class="home-card" href="workspaces/#clone-mode"><span class="home-card-mark" aria-hidden="true">04</span><h3>Клонировать вместо монтирования</h3><p>Оставьте репозиторий на хосте read-only и забирайте коммиты агента из приватного клона в госте.</p><span class="home-card-link">Руководство по клону →</span></a>
</div>
</section>

<section class="home-section" aria-labelledby="journey-title">
<div class="home-section-heading"><div><p class="home-kicker">Путь разработчика</p><h2 id="journey-title">От checkout до ограниченного workflow</h2></div><p>Настраивайте новую машину по порядку. Каждый шаг ведёт к требованиям и ограничениям, необходимым для решения.</p></div>
<div class="home-journey">
<article class="journey-step"><span class="journey-index">01 · Подготовка</span><h3>Проверьте платформу</h3><p>Изучите поддержку host, toolchain и runtime-компоненты.</p><a href="requirements/">Системные требования →</a></article>
<article class="journey-step"><span class="journey-index">02 · Запуск</span><h3>Установите и загрузите VM</h3><p>Установите альфа-бинарники и запустите daemon с VM-backend.</p><a href="quickstart/">Быстрый старт →</a></article>
<article class="journey-step"><span class="journey-index">03 · Настройка</span><h3>Подключите workflow</h3><p>Изучите агентов, файлы, credentials и kits.</p><a href="agents/">Руководство по агентам →</a></article>
<article class="journey-step"><span class="journey-index">04 · Проверка</span><h3>Оцените границу</h3><p>Отличайте успех команды от VM- и security-проверки.</p><a href="security/">Модель безопасности →</a></article>
</div>
</section>

<section class="home-section" aria-labelledby="status-title">
<div class="home-status">
<div class="home-status-copy"><p class="home-kicker">Текущее состояние проекта</p><h2 id="status-title">Rheic загружает microVM на macOS ARM64.</h2><p>Альфа Sandboxes выпущена: <code>rsbx</code> v0.0.49 и <code>sandboxesd</code> v0.0.56 публикуются с <code>SHA256SUMS</code> и SLSA-attestations, а daemon загружает настоящие microVM на macOS ARM64 через containerd, nerdbox shim и libkrun. Live acceptance покрыла create, start, exec, stop, start, delete, изоляцию между VM, opt-in матрицы IPv6 и QUIC, registry broker и режим клона. Windows WHP, облачные команды (<code>move</code>, <code>ttl</code>, <code>volume</code>), вложенные Docker workloads внутри гостя и независимый внешний security review пока не поддерживаются.</p></div>
<ul class="home-status-list" aria-label="Статус возможностей">
<li><span class="status-dot" aria-hidden="true"></span><span>Альфа-бинарники<strong>Выпущены и проверены</strong></span></li>
<li><span class="status-dot" aria-hidden="true"></span><span>VM-путь macOS ARM64<strong>Проверен live</strong></span></li>
<li><span class="status-dot" aria-hidden="true"></span><span>Режим клона<strong>Проверен live</strong></span></li>
<li><span class="status-dot status-dot-off" aria-hidden="true"></span><span>Windows WHP, облачные команды и nested Docker<strong>Не поддерживаются</strong></span></li>
</ul>
</div>
</section>

<section class="home-section" aria-labelledby="topics-title">
<div class="home-section-heading"><div><p class="home-kicker">Структура документации</p><h2 id="topics-title">Найдите нужную тему</h2></div><p>Английские и русские руководства повторяют одинаковую структуру. Переключите язык в шапке страницы.</p></div>
<div class="home-directory">
<div class="directory-group"><h3>Сборка и настройка</h3><div class="directory-links"><a href="agents/">Агенты</a><a href="workspaces/">Workspace и файлы</a><a href="workspaces/#clone-mode">Приватный клон</a><a href="networking/">Сеть и порты</a><a href="credentials/">Credentials и вход</a><a href="kits/">Kits</a></div></div>
<div class="directory-group"><h3>Запуск и обслуживание</h3><div class="directory-links"><a href="docker/">Docker</a><a href="tui/">Терминальная панель</a><a href="troubleshooting/">Решение проблем</a><a href="settings/">Настройки</a></div></div>
<div class="directory-group"><h3>Устройство системы</h3><div class="directory-links"><a href="architecture/">Архитектура</a><a href="security/">Модель безопасности</a><a href="requirements/">Системные требования</a></div></div>
<div class="directory-group"><h3>Справочник команд</h3><div class="directory-links"><a href="cli/">CLI</a><a href="quickstart/">Быстрый старт</a></div></div>
</div>
</section>

<section class="home-section" aria-labelledby="faq-title">
<div class="home-section-heading"><div><p class="home-kicker">Перед началом</p><h2 id="faq-title">Частые вопросы</h2></div><a href="faq/">Все ответы →</a></div>
<div class="home-faq">
<details><summary>Быстрый старт запускает VM?</summary><p>Да. Основной путь — microVM: быстрый старт устанавливает альфа-бинарники, запускает daemon с VM-backend и выполняет <code>rsbx run shell .</code>, что загружает настоящую microVM на macOS ARM64. Режим state-only — резервный вариант для host-систем, где runtime-артефакты ещё не подготовлены: он проверяет локальную control plane и не запускает VM. См. <a href="quickstart/">Быстрый старт</a> и <a href="requirements/">Системные требования</a>.</p></details>
<details><summary>Можно ли запустить coding-агента внутри sandbox?</summary><p>VM lifecycle прошёл live acceptance на macOS ARM64, включая exec в запущенный гость. Авторизация провайдера и полные интерактивные сценарии каждого агента acceptance не прошли. Смотрите <a href="agents/">руководство по агентам</a> и <a href="requirements/">статус платформ</a>.</p></details>
<details><summary>Клонировать репозиторий или монтировать его?</summary><p>Монтируйте, если агент должен напрямую менять файлы на хосте. Используйте <code>rsbx run --clone</code>, когда репозиторий на хосте должен остаться read-only: агент коммитит в приватном клоне внутри гостя, а вы забираете эти коммиты через remote <code>sandbox-&lt;name&gt;</code>. Режиму клона нужен один настоящий Git-репозиторий, а образу — <code>git</code> вместе с <code>git daemon</code>. См. <a href="workspaces/#clone-mode">workspace</a>.</p></details>
<details><summary>Успешная команда подтверждает изоляцию?</summary><p>Нет. Ответ CLI подтверждает только результат указанной команды. Для VM-изоляции нужны отдельные live runtime и security evidence. См. <a href="security/">модель безопасности</a>.</p></details>
<details><summary>Готов ли Docker Engine внутри guest к запуску workloads?</summary><p>Опциональный guest Docker daemon запускается, но вложенные <code>docker run</code>, <code>docker load</code>, <code>docker build</code> и Compose блокируются ограничениями guest <code>unshare</code> в текущем runtime. См. <a href="docker/">Docker и Rheic</a>.</p></details>
</div>
</section>

<section class="home-section" aria-label="Продолжить чтение">
<div class="home-endcap"><div><h2>Начните с вашей машины.</h2><p>Проверьте требования, установите альфу и загрузите microVM.</p></div><a class="home-button" href="requirements/">Системные требования ↗</a></div>
</section>

</div>
