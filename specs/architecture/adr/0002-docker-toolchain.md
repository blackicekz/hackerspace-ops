# ADR 0002: Docker-owned toolchain

Status: accepted

The Python base image and development tools are pinned in the Dockerfile. Docker Compose is the
host-facing interface; shell scripts run only inside the Linux container. This makes runtime and
verification reproducible for residents on Windows or Linux without host Python, Bash, Make, or a
Python package manager. Compose is worthwhile even for one service because it provides one portable
command surface and a consistent development bind mount.
