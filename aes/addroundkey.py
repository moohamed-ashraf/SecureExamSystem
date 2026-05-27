"""AES AddRoundKey transformation."""

from __future__ import annotations

from typing import List


def add_round_key(state: List[int], round_key: List[int]) -> None:
    for i in range(16):
        state[i] ^= round_key[i]
