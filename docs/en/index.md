---
title: Gyrel Sandboxes
description: Documentation for local agent sandboxes, the native runtime and Docker sbx compatibility.
hide: [navigation, toc]
---
<div class="landing docs-home">
<section class="docs-hero">
  <div class="docs-hero-copy">
    <p class="section-label">Gyrel Sandboxes</p>
    <h1>Run coding agents in a local sandbox</h1>
    <p class="hero-intro">Run coding agents in a local VM. This site documents setup, the CLI reference, native runtime assets and the verified Docker <code>sbx</code> comparison.</p>
    <button class="hero-search" type="button" data-open-search aria-label="Search documentation"><span class="search-glass" aria-hidden="true"></span><span>Search documentation</span><kbd data-shortcut-mod>Ctrl</kbd><kbd>K</kbd></button>
    <div class="hero-actions"><a href="quickstart/">↗ &nbsp;Quickstart</a><a href="cli/">⌘ &nbsp;CLI reference</a><a href="comparison/">⇄ &nbsp;Docker comparison</a></div>
  </div>
  <div class="code-window" aria-label="Gyrel command example"><div class="code-tabs"><span class="code-tab-active">Terminal</span></div><pre><code><span class="code-comment"># Check the released CLI</span>
<span class="code-command">$</span> rsbx version

<span class="code-comment"># Start after configuring a VM backend</span>
<span class="code-command">$</span> rsbx run shell .

<span class="code-comment"># Inspect your local sandboxes</span>
<span class="code-command">$</span> rsbx ls</code></pre></div>
</section>
<section class="docs-section"><p class="section-label">Documentation</p><h2>Choose where to start</h2><p class="section-intro">Follow the setup path or jump directly to the part you need.</p><div class="docs-grid">
<a class="docs-card" href="quickstart/"><span class="card-icon" aria-hidden="true">⌁</span><h3>Get started</h3><p>Install the CLI and daemon, then prepare a compatible VM backend.</p><span class="card-link">Read the quickstart ↗</span></a>
<a class="docs-card" href="cli/"><span class="card-icon" aria-hidden="true">›_</span><h3>Use the CLI</h3><p>Find commands for running, inspecting and managing local sandboxes.</p><span class="card-link">Explore commands ↗</span></a>
<a class="docs-card" href="runtime/"><span class="card-icon" aria-hidden="true">▣</span><h3>Inspect the runtime</h3><p>Check the published shim, kernel and rootfs with their SHA-256 inventory.</p><span class="card-link">View runtime assets ↗</span></a>
<a class="docs-card" href="comparison/"><span class="card-icon" aria-hidden="true">⇄</span><h3>Compare with Docker sbx</h3><p>Read version-matched evidence, confirmed differences and open controls.</p><span class="card-link">See the comparison ↗</span></a>
<a class="docs-card" href="user-cases/"><span class="card-icon" aria-hidden="true">☰</span><h3>Work through user cases</h3><p>Run the exact alpha scenarios: review sandboxes, templates, credentials, approvals, and fail-closed refusals.</p><span class="card-link">Read the user cases ↗</span></a>
<a class="docs-card" href="alpha-testing/"><span class="card-icon" aria-hidden="true">⚕</span><h3>Report with a bundle</h3><p>One redacted diagnostic bundle makes a bug fixable. It never carries your secrets.</p><span class="card-link">Open the tester guide ↗</span></a>
</div></section>
<section class="docs-section journey"><p class="section-label">A practical path</p><h2>From install to evidence</h2><div class="journey-grid"><div><span>01</span><h3>Prepare</h3><p>Install the released components and configure your local backend.</p><a href="quickstart/">Setup guide ↗</a></div><div><span>02</span><h3>Run</h3><p>Start an owned sandbox in a private workspace with <code>rsbx</code>.</p><a href="cli/">CLI reference ↗</a></div><div><span>03</span><h3>Verify</h3><p>Check the platform scope and the live comparison before relying on parity.</p><a href="limits/">Security and limits ↗</a></div></div></section>
<section class="docs-section boundary"><p class="section-label">Current scope</p><h2>Know what is verified</h2><p>Gyrel is an alpha release. The full macOS ARM64 flow is live-verified end to end: VM lifecycle, template save/load, credentials with fail-closed substitution, approvals, kit policy, MCP registration, crash-safe journal recovery, and digest-verified managed artifacts. Native Linux and Windows hosts remain unverified. Complete Docker <code>sbx</code> parity claims are limited to the available evidence. The documentation distinguishes live evidence from planned behavior.</p><div class="boundary-links"><a href="limits/">Security and limits ↗</a><a href="comparison/">Comparison evidence ↗</a></div></section>
</div>
