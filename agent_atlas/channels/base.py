# -*- coding: utf-8 -*-
"""Channel base — doctor check contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


class Channel(ABC):
    name: str = ""
    description: str = ""
    backends: List[str] = []
    tier: int = 0  # 0=zero-config, 1=needs login

    active_backend: Optional[str] = None

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        ...

    @abstractmethod
    def check(self, config=None) -> Tuple[str, str]:
        """Return (status, message) where status is ok|warn|off|error."""
        ...
