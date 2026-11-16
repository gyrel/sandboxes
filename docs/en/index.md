---
title: Overview
description: Install the released Sandboxes alpha by Rheic and boot real microVMs on macOS ARM64. Quick start, task guides, platform status, CLI, and security boundaries.
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
<p class="home-eyebrow">Rheic docs · Sandboxes alpha released · macOS ARM64 microVMs</p>

<h1 id="home-title">A local boundary for coding agents.</h1>

<p class="home-lede">Run coding agents in local microVMs on macOS ARM64. Install the alpha, configure the daemon, and start a sandbox from your terminal.</p>

<div class="home-actions">
<a class="home-button" href="quickstart/">Start with the quick start <span aria-hidden="true">↗</span></a>
<a class="home-button home-button-secondary" href="cli/">Browse the CLI reference</a>
</div>

<label class="home-search-trigger" for="__search"><span>Search the documentation</span><kbd>/</kbd></label>

<p class="home-footnote">Alpha software · microVM path validated live on macOS ARM64 · Windows WHP, cloud, and nested Docker remain out of scope or blocked</p>
</div>

<div class="home-terminal" aria-label="Rheic local command examples">
<div class="home-terminal-head"><span class="home-terminal-brand"><img src="assets/rheic-shark.png" alt=""><strong>Boot a microVM</strong></span><span class="home-terminal-lang">rsbx</span></div>
<div class="home-terminal-code" markdown>
```sh
rsbx version
rsbx run shell .
rsbx ls
```
</div>
<div class="home-terminal-foot">Install the CLI and configure the VM backend first. <a href="quickstart/">Follow the quick start →</a></div>
</div>
</section>

<section class="home-section" aria-labelledby="choose-title">
<div class="home-section-heading"><div><p class="home-kicker">Choose a starting point</p><h2 id="choose-title">What are you here to do?</h2></div><p>Use the guide for your task, then check its prerequisites and known limits before running commands.</p></div>
<div class="home-path-grid">
<a class="home-card" href="quickstart/"><span class="home-card-mark" aria-hidden="true">01</span><h3>Install the alpha and boot a microVM</h3><p>Install the released binaries, start the daemon with the VM backend, then attach a shell to a guest.</p><span class="home-card-link">Quick start →</span></a>
<a class="home-card" href="workspaces/"><span class="home-card-mark" aria-hidden="true">02</span><h3>Prepare an agent workspace</h3><p>Understand how workspace paths, file operations, and sandbox lifecycle fit together.</p><span class="home-card-link">Workspace guide →</span></a>
<a class="home-card" href="networking/"><span class="home-card-mark" aria-hidden="true">03</span><h3>Review network boundaries</h3><p>See the default allow-all profile, deny precedence, HTTP policy conditions, and published ports.</p><span class="home-card-link">Network guide →</span></a>
<a class="home-card" href="workspaces/#clone-mode"><span class="home-card-mark" aria-hidden="true">04</span><h3>Clone instead of mounting</h3><p>Keep the host repository read-only and fetch agent commits from a private in-guest clone.</p><span class="home-card-link">Clone guide →</span></a>
</div>
</section>

<section class="home-section" aria-labelledby="journey-title">
<div class="home-section-heading"><div><p class="home-kicker">Developer journey</p><h2 id="journey-title">From checkout to a bounded workflow</h2></div><p>Move in order when setting up a new machine. Each step links to the details needed to make a decision.</p></div>
<div class="home-journey">
<article class="journey-step"><span class="journey-index">01 · Prepare</span><h3>Check your platform</h3><p>Review host support, toolchain, and runtime inputs.</p><a href="requirements/">System requirements →</a></article>
<article class="journey-step"><span class="journey-index">02 · Start</span><h3>Install and boot</h3><p>Install the alpha binaries and start the daemon with the VM backend.</p><a href="quickstart/">Quick start →</a></article>
<article class="journey-step"><span class="journey-index">03 · Configure</span><h3>Connect the workflow</h3><p>Read about agents, files, credentials, and kits.</p><a href="agents/">Agent guide →</a></article>
<article class="journey-step"><span class="journey-index">04 · Verify</span><h3>Check the boundary</h3><p>Separate command success from VM and security acceptance.</p><a href="security/">Security model →</a></article>
</div>
</section>

<section class="home-section" aria-labelledby="status-title">
<div class="home-status">
<div class="home-status-copy"><p class="home-kicker">Current project status</p><h2 id="status-title">Rheic boots microVMs on macOS ARM64.</h2><p>The Sandboxes alpha is released: <code>rsbx</code> v0.0.54 and <code>sandboxesd</code> v0.0.62 ship with <code>SHA256SUMS</code> and SLSA provenance, and the daemon boots real microVMs on macOS ARM64 through containerd, the nerdbox shim, and libkrun. The CLI adds daemon lifecycle commands and Docker <code>sbx</code>-compatible JSON for core commands. Live acceptance covered create, start, exec, stop, start, delete, cross-VM isolation, the IPv6 and QUIC opt-in matrices, and clone mode. Windows WHP is not implemented, cloud commands (<code>move</code>, <code>ttl</code>, <code>volume</code>) are out of scope, nested Docker workloads inside the guest remain blocked, and no independent external security review has been completed.</p></div>
<ul class="home-status-list" aria-label="Capability status">
<li><span class="status-dot" aria-hidden="true"></span><span>Alpha binaries<strong>Released and verified</strong></span></li>
<li><span class="status-dot" aria-hidden="true"></span><span>macOS ARM64 microVM path<strong>Validated live</strong></span></li>
<li><span class="status-dot" aria-hidden="true"></span><span>Clone mode<strong>Validated live</strong></span></li>
<li><span class="status-dot status-dot-off" aria-hidden="true"></span><span>Windows WHP, cloud commands, and nested Docker<strong>Not implemented or out of scope</strong></span></li>
</ul>
</div>
</section>

<section class="home-section" aria-labelledby="topics-title">
<div class="home-section-heading"><div><p class="home-kicker">Documentation map</p><h2 id="topics-title">Find a topic</h2></div><p>English and Russian guides share the same sections. Use the language control in the header to switch.</p></div>
<div class="home-directory">
<div class="directory-group"><h3>Build and configure</h3><div class="directory-links"><a href="agents/">Agents</a><a href="workspaces/">Workspaces and files</a><a href="workspaces/#clone-mode">Private clone</a><a href="networking/">Network and ports</a><a href="credentials/">Credentials and sign-in</a><a href="kits/">Kits</a></div></div>
<div class="directory-group"><h3>Run and maintain</h3><div class="directory-links"><a href="docker/">Docker</a><a href="tui/">Terminal dashboard</a><a href="troubleshooting/">Troubleshooting</a><a href="settings/">Settings</a></div></div>
<div class="directory-group"><h3>Understand the system</h3><div class="directory-links"><a href="architecture/">Architecture</a><a href="security/">Security model</a><a href="requirements/">System requirements</a></div></div>
<div class="directory-group"><h3>Look up commands</h3><div class="directory-links"><a href="cli/">CLI reference</a><a href="quickstart/">Quick start</a></div></div>
</div>
</section>

<section class="home-section" aria-labelledby="faq-title">
<div class="home-section-heading"><div><p class="home-kicker">Before you begin</p><h2 id="faq-title">Common questions</h2></div><a href="faq/">Read all FAQs →</a></div>
<div class="home-faq">
<details><summary>Does the quick start launch a VM?</summary><p>Yes. The microVM path is the primary path: the quick start installs the alpha binaries, starts the daemon with the VM backend, and runs <code>rsbx run shell .</code>, which boots a real microVM on macOS ARM64. State-only mode is a fallback for hosts that do not have the runtime assets yet; it checks the local control plane and does not boot a VM. See <a href="quickstart/">Quick start</a> and <a href="requirements/">System requirements</a>.</p></details>
<details><summary>Can I run a coding agent inside the sandbox?</summary><p>The VM lifecycle passed live acceptance on macOS ARM64, including exec into a running guest. Provider authentication and complete interactive workflows for every agent have not passed acceptance. Check the <a href="agents/">agent guide</a> and <a href="requirements/">platform status</a>.</p></details>
<details><summary>Should I clone a repository or mount it?</summary><p>Mount it when the agent should edit host files directly. Use <code>rsbx run --clone</code> when the host repository must stay read-only: the agent commits in a private in-guest clone and you fetch those commits through the <code>sandbox-&lt;name&gt;</code> remote. Clone mode requires one real Git repository, and the image needs <code>git</code> with <code>git daemon</code>. The host remote URL carries a random per-sandbox token. See <a href="workspaces/#clone-mode">workspaces</a>.</p></details>
<details><summary>Is outbound network access allowed by default?</summary><p>Yes. New sandboxes use the <code>allow-all</code> egress profile, matching Docker <code>sbx</code>. Explicit deny rules and organization deny rules still take precedence, and fail-closed controls are unchanged. Start with <code>--policy-profile deny-all</code> when a task should not reach the network. HTTP policy conditions for method, path glob, and query exist in the gateway policy layer; <code>rsbx</code> cannot author them yet, and live gateway enforcement of those conditions remains unverified. See <a href="networking/">network and ports</a>.</p></details>
<details><summary>Does a successful command prove isolation?</summary><p>No. A CLI response confirms only the operation reported by that command. VM isolation needs its own live runtime and security evidence. See the <a href="security/">security model</a>.</p></details>
<details><summary>Is Docker Engine inside the guest ready for workloads?</summary><p>The opt-in guest Docker daemon can start, but nested <code>docker run</code>, <code>docker load</code>, <code>docker build</code>, and Compose are blocked by guest <code>unshare</code> restrictions in the current runtime. See <a href="docker/">Docker and Rheic</a>.</p></details>
</div>
</section>

<section class="home-section" aria-label="Continue reading">
<div class="home-endcap"><div><h2>Start with the machine you have.</h2><p>Check the prerequisites, install the alpha, then boot a microVM.</p></div><a class="home-button" href="requirements/">Review system requirements ↗</a></div>
</section>

</div>
