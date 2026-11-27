---
title: Gyrel Sandboxes
description: Документация локальных sandbox для агентов, нативного runtime и совместимости с Docker sbx.
hide: [navigation, toc]
---
<div class="landing docs-home">
<section class="docs-hero">
  <div class="docs-hero-copy">
    <p class="section-label">Gyrel Sandboxes</p>
    <h1>Запускайте coding-агентов в локальной песочнице</h1>
    <p class="hero-intro">Запускайте coding-агентов в локальной VM. На сайте собраны установка, справочник CLI, нативный runtime и проверенное сравнение с Docker <code>sbx</code>.</p>
    <button class="hero-search" type="button" data-open-search aria-label="Поиск по документации"><span class="search-glass" aria-hidden="true"></span><span>Поиск по документации</span><kbd data-shortcut-mod>Ctrl</kbd><kbd>K</kbd></button>
    <div class="hero-actions"><a href="quickstart/">↗ &nbsp;Быстрый старт</a><a href="cli/">⌘ &nbsp;Справочник CLI</a><a href="comparison/">⇄ &nbsp;Сравнение с Docker</a></div>
  </div>
  <div class="code-window" aria-label="Пример команд Gyrel"><div class="code-tabs"><span class="code-tab-active">Терминал</span></div><pre><code><span class="code-comment"># Проверьте установленный CLI</span>
<span class="code-command">$</span> rsbx version

<span class="code-comment"># Запустите после настройки VM backend</span>
<span class="code-command">$</span> rsbx run shell .

<span class="code-comment"># Посмотрите локальные sandbox</span>
<span class="code-command">$</span> rsbx ls</code></pre></div>
</section>
<section class="docs-section"><p class="section-label">Документация</p><h2>С чего начать</h2><p class="section-intro">Пройдите путь настройки или сразу откройте нужный раздел.</p><div class="docs-grid">
<a class="docs-card" href="quickstart/"><span class="card-icon" aria-hidden="true">⌁</span><h3>Начало работы</h3><p>Установите CLI и daemon, затем подготовьте совместимый VM backend.</p><span class="card-link">Открыть инструкцию ↗</span></a>
<a class="docs-card" href="cli/"><span class="card-icon" aria-hidden="true">›_</span><h3>Команды CLI</h3><p>Запуск, проверка и управление локальными sandbox через <code>rsbx</code>.</p><span class="card-link">Смотреть команды ↗</span></a>
<a class="docs-card" href="runtime/"><span class="card-icon" aria-hidden="true">▣</span><h3>Нативный runtime</h3><p>Проверьте опубликованные shim, kernel и rootfs по SHA-256 inventory.</p><span class="card-link">Смотреть компоненты ↗</span></a>
<a class="docs-card" href="comparison/"><span class="card-icon" aria-hidden="true">⇄</span><h3>Сравнение с Docker sbx</h3><p>Согласованные по версиям доказательства, подтверждённые различия и открытые проверки.</p><span class="card-link">Читать сравнение ↗</span></a>
<a class="docs-card" href="user-cases/"><span class="card-icon" aria-hidden="true">☰</span><h3>Пользовательские кейсы</h3><p>Точные сценарии альфы: песочницы для ревью, шаблоны, credentials, согласования и честные отказы.</p><span class="card-link">К кейсам ↗</span></a>
<a class="docs-card" href="alpha-testing/"><span class="card-icon" aria-hidden="true">⚕</span><h3>Отчёт с бандлом</h3><p>Один очищенный диагностический бандл делает баг исправимым. Секреты в него не попадают.</p><span class="card-link">Гайд тестировщика ↗</span></a>
</div></section>
<section class="docs-section journey"><p class="section-label">Практический путь</p><h2>От установки к проверке</h2><div class="journey-grid"><div><span>01</span><h3>Подготовьте</h3><p>Установите опубликованные компоненты и настройте локальный backend.</p><a href="quickstart/">Инструкция ↗</a></div><div><span>02</span><h3>Запустите</h3><p>Создайте собственный sandbox в приватном workspace через <code>rsbx</code>.</p><a href="cli/">Команды CLI ↗</a></div><div><span>03</span><h3>Проверьте</h3><p>Узнайте границы поддержки и статус сравнения с Docker.</p><a href="limits/">Безопасность и ограничения ↗</a></div></div></section>
<section class="docs-section boundary"><p class="section-label">Текущий статус</p><h2>Что уже проверено</h2><p>Gyrel — alpha-версия. Полный macOS ARM64-цикл проверен вживую от начала до конца: жизненный цикл VM, save/load шаблонов, credentials с fail-closed подстановкой, согласования, kit-политика, регистрация MCP, crash-safe journal и managed-артефакты с проверкой дайджестов. Native Linux и Windows остаются непроверенными. Заявления о полной совместимости с Docker <code>sbx</code> ограничены имеющимися свидетельствами. Документация отделяет живые проверки от планов.</p><div class="boundary-links"><a href="limits/">Безопасность и ограничения ↗</a><a href="comparison/">Результаты сравнения ↗</a></div></section>
</div>
