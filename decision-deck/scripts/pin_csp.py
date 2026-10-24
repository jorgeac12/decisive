#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jorge Oliveira. Part of Decisive: https://github.com/jorgeac12/decisive
"""Maintainer tool: pin the runtime <script> of a deck or template by SHA-256 in its CSP.

Run after editing the runtime script in assets/template.html:
    python scripts/pin_csp.py assets/template.html

The CSP allows only this exact script to run. Any other inline script or
on* handler that ends up in a deck (for example through prompt injection in
the source documents) is blocked by the browser.
"""
import base64
import hashlib
import re
import sys

RUNTIME = re.compile(r"<script>(.*?)</script>", re.S)
CSP = re.compile(r"script-src '[^']*'")


def runtime_hash(html: str) -> str:
    scripts = RUNTIME.findall(html)
    if len(scripts) != 1:
        raise SystemExit(f"expected exactly 1 runtime <script>, found {len(scripts)}")
    digest = hashlib.sha256(scripts[0].encode("utf-8")).digest()
    return "sha256-" + base64.b64encode(digest).decode()


def main(path: str) -> None:
    html = open(path, encoding="utf-8").read()
    h = runtime_hash(html)
    new, n = CSP.subn(f"script-src '{h}'", html)
    if n != 1:
        raise SystemExit("CSP meta with script-src not found")
    open(path, "w", encoding="utf-8").write(new)
    print(f"pinned {h} in {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: pin_csp.py <template.html>")
    main(sys.argv[1])
