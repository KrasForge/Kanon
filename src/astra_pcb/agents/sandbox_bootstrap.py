"""Trusted bootstrap inside an empty Linux namespace. No third-party Python packages."""

import ctypes
import errno
import resource
import runpy


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024 * 1024, 8 * 1024 * 1024))
    library = ctypes.CDLL("libseccomp.so.2")
    library.seccomp_init.argtypes = [ctypes.c_uint32]
    library.seccomp_init.restype = ctypes.c_void_p
    library.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    library.seccomp_rule_add.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_uint,
    ]
    library.seccomp_load.argtypes = [ctypes.c_void_p]
    library.seccomp_release.argtypes = [ctypes.c_void_p]
    context = library.seccomp_init(0x7FFF0000)  # SCMP_ACT_ALLOW
    if not context:
        raise RuntimeError("Cannot initialize seccomp")
    try:
        for name in (
            "execve",
            "execveat",
            "fork",
            "vfork",
            "clone",
            "clone3",
            "socket",
            "ptrace",
            "mount",
            "umount2",
            "pivot_root",
            "unshare",
            "setns",
        ):
            syscall = library.seccomp_syscall_resolve_name(name.encode())
            if syscall < 0 or library.seccomp_rule_add(
                context, 0x00050000 | errno.EPERM, syscall, 0
            ):
                raise RuntimeError("Cannot install required syscall restriction")
        if library.seccomp_load(context):
            raise RuntimeError("Cannot enforce syscall restrictions")
    finally:
        library.seccomp_release(context)
    runpy.run_path("/worker.py", run_name="__main__")


if __name__ == "__main__":
    main()
