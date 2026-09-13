# Reviewer runtime isolation

`agents.sandbox.isolated_call` is a Linux-only, fail-closed executor for a trusted
standard-library Python reviewer adapter. It uses bubblewrap namespaces and a post-startup
libseccomp filter. The launcher never falls back to an unsandboxed process if required
kernel features, bubblewrap or libseccomp are unavailable.

The namespace starts empty. It receives only a read-only Python runtime/library tree,
a frozen copy of the trusted worker and optional read-only evidence at `/evidence`.
No host home directory, credentials, desktop sockets, live KiCad transport or source write
mount is present. The environment is cleared and all capabilities are dropped. Private
network/PID/IPC namespaces and a new session isolate the process. Seccomp denies socket,
exec, fork/clone, ptrace and namespace/mount operations after the interpreter starts.
This prevents launching a shell even if executable bytes are supplied as input data.

Input travels through stdin; bounded stdout contains the response. CPU, memory, file size
and wall time are bounded. The parent kills the process group on timeout. `/tmp` is an
isolated disposable tmpfs. The worker is deployment-owned code, not a model-supplied shell
or command. Do not mount arbitrary host directories or change the fixed policy for a model
request. A remote model gateway can exchange data through the trusted harness; account
credentials and model/API transport do not belong inside the source-review sandbox.

The real integration test attempts source modification, socket creation, child execution
and credential access and verifies denial while allowing frozen evidence reads. A separate
Ubuntu 22.04 CI job qualifies the required OS boundary; general core CI skips the native
probe when its platform cannot supply the required isolation. Missing runtime isolation
is always an execution error for actual reviews, never an approved review.

This policy follows the capability-based deployment requirements in the
[bubblewrap security documentation](https://github.com/containers/bubblewrap) and the
[libseccomp API](https://man7.org/linux/man-pages/man3/seccomp_rule_add.3.html).
