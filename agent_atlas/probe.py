# -*- coding: utf-8 -*-
"""Lightweight command probes for doctor."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Sequence


@dataclass
class ProbeResult:
    status: str  # ok | missing | broken | timeout
    output: str = ""
    hint: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def probe_command(
    cmd: str,
    args: Sequence[str] = (),
    *,
    timeout: float = 15,
    package: str = "",
) -> ProbeResult:
    path = which(cmd)
    if not path:
        hint = f"Install: {package}" if package else f"Command not found: {cmd}"
        return ProbeResult("missing", hint=hint)

    try:
        proc = subprocess.run(
            [cmd, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return ProbeResult("broken", hint=f"{cmd} exists on PATH but failed to start")
    except subprocess.TimeoutExpired:
        return ProbeResult("timeout", hint=f"{cmd} timed out after {timeout}s")

    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0:
        return ProbeResult("ok", output=out.strip())
    return ProbeResult("broken", output=out.strip(), hint=f"{cmd} exited {proc.returncode}")


def http_ok(url: str, timeout: float = 10) -> bool:
    try:
        import urllib.request

        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "agent-atlas/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= getattr(resp, "status", 200) < 400
    except Exception:
        return False
