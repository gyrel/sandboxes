# Architecture

Gyrel is a local control plane for sandboxed agent sessions. Its components have separate responsibilities and must be built from compatible module versions.

```text
rsbx CLI / terminal dashboard
          │ local API through sandboxes-go-sdk
          ▼
      sandboxesd ───── host credential vault
          │
          ├── runtime adapter ── microVM ── guest agent
          └── network gateway ─── guest network policy
```

## Control plane

The CLI calls the local daemon through the official Go SDK and the public API module. The daemon owns sandbox metadata and coordinates runtime, workspace, policy, and credential operations. In state-only mode, it can manage metadata but cannot boot a VM. A configured runtime backend is required for guest execution.

## Runtime and guest

The VM runtime, guest image, shim, and helper binaries are external, version-sensitive inputs. A limited VM-backed lifecycle is validated on macOS Apple silicon. A separate Linux ARM64 guest task passed managed-containerd detach/reattach in an Ubuntu Lima/QEMU VM with nested KVM hosted by macOS. This does not qualify a native Linux host or rootless operation; Windows WHP is not implemented. The agent runs in the guest; workspace mounts define what host project data it can access.

## Network boundary

When configured, a separate gateway enforces supported guest egress policy. New sandboxes use the `allow-all` egress profile by default, matching Docker `sbx`; explicit deny rules and organization deny precedence still apply, and `deny-all` remains selectable. A missing gateway does not mean unrestricted connectivity: network functionality may be unavailable. Policy syntax accepted by the CLI is not proof that a particular gateway build enforces it. See [Network and ports](networking.md).

## Credentials

Secrets are stored in the host OS credential vault. The daemon resolves only supported, explicitly requested flows; a stored credential is not automatically passed to a guest. Docker account authentication is not the same as Docker Engine access from inside a guest. See [Credentials](credentials.md) and [Docker](docker.md).

## State of validation

Gyrel is alpha software. Do not treat a successful CLI response or a state-only daemon as evidence of VM isolation. Windows WHP is not implemented, cloud commands are out of scope, and independent security review, signing, and upgrade/rollback validation remain open gates. See [Security](security.md) for the current limits.
