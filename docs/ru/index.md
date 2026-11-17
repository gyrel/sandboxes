---
title: Rheic Sandboxes
description: Локальные песочницы для агентов, native ARM64 bundle и сравнение с Docker sbx.
hide: [navigation, toc]
---
<div class="landing" markdown>
<section class="hero"><div class="hero-copy" markdown>
<p class="eyebrow">RHEIC / SANDBOXES ALPHA / ARM64 BUNDLES</p><h1>Локальные VM для coding-агентов.</h1>
<p class="lede">Запускайте агентов через <code>rsbx</code>. Проверьте native runtime и узнайте, где Rheic совпадает с Docker <code>sbx</code>.</p>
<a class="primary-link" href="quickstart/">Начать ↗</a>
<p class="proof">CLI v0.0.54 · daemon v0.0.62 · runtime v0.0.36 · ARM64 guest boot проверен</p>
</div><div class="terminal"><div class="terminal-top">● ● ● <span>Terminal</span></div><pre><code><span class="prompt">$</span> rsbx version
<span class="muted">rsbx version v0.0.54</span>
<span class="prompt">$</span> rsbx run shell .
<span class="muted"># нужен настроенный VM backend</span></code></pre></div></section>
<section class="reveal-section"><p data-reveal><span>Одна</span> <span>команда</span> <span>для</span> <span>старта.</span><br><span>Доказательства</span> <span>для</span> <span>каждого</span> <span>утверждения.</span></p></section>
<section class="page-section"><p class="eyebrow">РАЗДЕЛЫ</p><h2>С чего начать</h2><div class="card-grid">
<a class="feature-card" href="quickstart/"><span>01 / СТАРТ</span><h3>Запустить sandbox</h3><p>Установить CLI и подключить VM backend.</p><b>Быстрый старт ↗</b></a>
<a class="feature-card" href="comparison/"><span>02 / СРАВНЕНИЕ</span><h3>Проверить parity с Docker</h3><p>Версии, расхождения и непроверенные сценарии.</p><b>Сравнение ↗</b></a>
<a class="feature-card" href="runtime/"><span>03 / ПРОВЕРКА</span><h3>Изучить native assets</h3><p>Скачать shim, kernel, rootfs и SHA-256 inventory.</p><b>Runtime bundles ↗</b></a>
</div></section>
<section class="status-panel"><p class="eyebrow">ТЕКУЩИЙ СТАТУС</p><h2>VM boot проверен.<br>Полный parity с <code>sbx</code> ещё открыт.</h2><p>Cloud, OCI kits, часть команд управления, native Linux host и полная совместимость Docker workloads остаются открытыми.</p><a href="limits/">Ограничения ↗</a></section>
<section class="page-section faq"><p class="eyebrow">ВОПРОСЫ</p><h2>Перед запуском агента</h2>
<details><summary>Rheic уже заменяет Docker sbx?</summary><p>Нет. См. <a href="comparison/">сравнение</a> команд и пробелов.</p></details>
<details><summary>Достаточно установить rsbx?</summary><p>Нет. Нужны совместимый daemon и настроенный native runtime. См. <a href="quickstart/">быстрый старт</a>.</p></details>
<details><summary>Shim, kernel и rootfs опубликованы?</summary><p>Да, в обоих ARM64-архивах runtime v0.0.36.</p></details>
<details><summary>Есть cloud sandboxes?</summary><p>Нет. Rheic сейчас работает с локальным daemon.</p></details>
<details><summary>Есть attestation native-архивов?</summary><p>Есть SHA-256 и точный inventory, но нет независимого provenance attestation.</p></details>
<details><summary>Какие host-платформы квалифицированы?</summary><p>macOS ARM64 проверена локально. Linux ARM64 guest boot прошёл в nested KVM; native Linux host и rootless ещё открыты.</p></details>
</section><section class="final-cta"><h2>Начните с проверенного пути.</h2><a class="primary-link" href="quickstart/">Начать ↗</a></section></div>
