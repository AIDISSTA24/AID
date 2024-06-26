"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

import LightBase


class TypedLockState(TypedDict):
    """Lock state type definition."""

    on: bool


class TypedLock(TypedDict):
    """Lock type definition."""

    state: TypedLockState


class Lock(LightBase):
    """Lock class."""

    raw: TypedLock

    @property
    def is_locked(self) -> bool:
        """State of lock."""
        return self.raw["state"]["on"]
