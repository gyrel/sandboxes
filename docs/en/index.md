---
title: Rheic Sandboxes
description: Local agent sandboxes, native ARM64 runtime bundles and an evidence-led Docker sbx comparison.
hide: [navigation, toc]
---
<div class="landing" markdown>
<section class="hero"><div class="hero-copy" markdown>
<p class="eyebrow">RHEIC / SANDBOXES ALPHA / ARM64 BUNDLES</p>
<h1>Local VMs for coding agents.</h1>
<p class="lede">Run agents with <code>rsbx</code>. Inspect the native runtime, then see exactly where Rheic matches Docker <code>sbx</code> today.</p>
<a class="primary-link" href="quickstart/">Get started ↗</a>
<p class="proof">CLI v0.0.54 · daemon v0.0.62 · runtime v0.0.36 · ARM64 guest boot verified</p>
</div><div class="terminal"><div class="terminal-top">● ● ● <span>Terminal</span></div><pre><code><span class="prompt">$</span> rsbx version
<span class="muted">rsbx version v0.0.54</span>
<span class="prompt">$</span> rsbx run shell .
<span class="muted"># requires a configured VM backend</span></code></pre></div></section>
<section class="reveal-section"><p data-reveal><span>One</span> <span>command</span> <span>to</span> <span>start.</span><br><span>Evidence</span> <span>for</span> <span>every</span> <span>claim.</span></p></section>
<section class="page-section"><p class="eyebrow">EXPLORE</p><h2>Choose your path</h2><div class="card-grid">
<a class="feature-card" href="quickstart/"><span>01 / START</span><h3>Boot a local sandbox</h3><p>Install the CLI and connect a VM backend.</p><b>Quick start ↗</b></a>
<a class="feature-card" href="comparison/"><span>02 / COMPARE</span><h3>Check Docker parity</h3><p>Version matched evidence, confirmed gaps and unknowns.</p><b>Comparison ↗</b></a>
<a class="feature-card" href="runtime/"><span>03 / VERIFY</span><h3>Inspect native assets</h3><p>Download the shim, kernel and rootfs with SHA-256 inventory.</p><b>Runtime bundles ↗</b></a>
</div></section>
<section class="status-panel"><p class="eyebrow">CURRENT BOUNDARY</p><h2>VM boot is verified.<br>Full <code>sbx</code> parity remains open.</h2><p>Cloud operations, OCI kits, parts of management CLI, native Linux host qualification and complete Docker workload parity are open.</p><a href="limits/">Read the limits ↗</a></section>
<section class="page-section faq"><p class="eyebrow">QUESTIONS</p><h2>Before you run an agent</h2>
<details><summary>Is Rheic a drop in replacement for Docker sbx?</summary><p>No. See the <a href="comparison/">comparison</a> for supported commands and gaps.</p></details>
<details><summary>Does rsbx alone start a VM?</summary><p>No. Configure a compatible daemon and native runtime first. See <a href="quickstart/">get started</a>.</p></details>
<details><summary>Are shim, kernel and rootfs published?</summary><p>Yes, in both ARM64 archives of runtime v0.0.36.</p></details>
<details><summary>Are cloud sandboxes supported?</summary><p>No. Rheic currently uses a local daemon.</p></details>
<details><summary>Are native archives attested?</summary><p>They have SHA-256 checksums and exact inventories, not an independent provenance attestation.</p></details>
<details><summary>Which hosts are qualified?</summary><p>macOS ARM64 has local VM acceptance. Linux ARM64 guest boot passed nested KVM; native Linux host and rootless qualification remain open.</p></details>
</section><section class="final-cta"><h2>Start with the verified path.</h2><a class="primary-link" href="quickstart/">Get started ↗</a></section></div>
