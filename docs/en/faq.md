# Frequently asked questions

Gyrel is alpha software. This page separates what Docker Sandboxes documents from what has been implemented and validated in Gyrel.

## Does Docker Sandboxes use full microVMs?

Docker documents one lightweight microVM and Linux kernel per agent, with a separate Docker Engine inside the VM. The hypervisor is the primary isolation boundary; host workspaces and other integrations cross that boundary only when explicitly shared. See Docker's [isolation layers](https://docs.docker.com/ai/sandboxes/security/isolation/) and [architecture](https://docs.docker.com/ai/sandboxes/architecture/) guides. “MicroVM” describes the virtualization boundary; it is not a guarantee that every configuration or integration is risk-free.

Gyrel also targets a microVM boundary, but it does not currently claim Docker parity or complete security qualification. A limited VM-backed lifecycle passed on macOS ARM64. A separate Linux ARM64 guest-task test ran under Lima/QEMU with nested KVM on macOS and survived managed-containerd detach and reattach. This does not qualify a native Linux host or rootless operation. Windows WHP is not implemented, cloud commands are out of scope for the local alpha, and independent security review remains open. See the [Gyrel architecture](architecture.md), [platform requirements](requirements.md), and [security model](security.md).

## Does the quick start launch a VM?

Yes. The primary path installs the alpha binaries, starts the daemon with the VM backend, and runs `rsbx run shell .`, which boots a real microVM on macOS ARM64. State-only mode remains a labelled fallback for hosts without the runtime artifacts and does not boot a VM. See [system requirements](requirements.md) and [quick start](quickstart.md).

## Can I run a coding agent inside a Gyrel sandbox?

The CLI and runtime include agent and exec paths, and limited VM-backed lifecycle acceptance passed on macOS ARM64. Full interactive workflows for every agent and platform have not passed acceptance. See the [agent guide](agents.md) and [platform status](requirements.md).

## Is outbound network access allowed by default?

Yes. New sandboxes use the `allow-all` egress profile (TCP and UDP to `0.0.0.0/0`), matching Docker `sbx`. Explicit deny rules and organization deny rules still take precedence, and fail-closed controls are unchanged. Start a sandbox with `--policy-profile deny-all` when a task should not reach the network. HTTP policy conditions for method, path glob, and query exist in the gateway policy layer, but `rsbx` cannot author them yet and live gateway enforcement of those conditions remains unverified. See [network and ports](networking.md).

## Should I mount a repository or use clone mode?

Mount it when the agent should edit your working tree directly. Use `rsbx run --clone` when the host repository must stay read-only: the source is mounted read-only, the agent commits in a private clone inside the guest, and you fetch those commits through the host remote `sandbox-<name>`. The remote URL carries a random per-sandbox token that is regenerated on every start. Clone mode requires exactly one real Git repository (a linked worktree with a `.git` file is rejected) and an image that provides `git` and `git daemon`; a non-empty destination is rejected. The endpoint exists only while the sandbox runs, and a user-edited remote is preserved rather than overwritten. See [workspaces and files](workspaces.md#clone-mode).

## Does a successful command prove isolation?

No. A successful CLI response confirms only that command's result. VM isolation requires separate live runtime and security evidence. See the [security model](security.md).

## Is Docker Engine inside the guest ready for workloads?

The opt-in guest Docker daemon can start, but nested `docker run`, `docker load`, `docker build`, and Compose are blocked by guest `unshare` restrictions in the current runtime. This is not the Docker Engine workflow documented by Docker Sandboxes. See [Docker and Gyrel](docker.md).

## Can the guest access my host files or Docker daemon?

Only explicitly configured workspace paths are shared with the guest. A writable workspace lets guest processes change those host files, so mount only what the task needs. The host Docker socket is not mounted. See [workspaces and files](workspaces.md) and the [security model](security.md).
