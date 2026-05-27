"""AES-128 key expansion (key schedule)."""

from __future__ import annotations

from typing import List

from aes.subbytes import SBOX

RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]


def expand_key(key: bytes, num_rounds: int = 10) -> List[List[int]]:
    key_words = []
    for i in range(4):
        key_words.append(list(key[4 * i : 4 * i + 4]))

    for i in range(4, 4 * (num_rounds + 1)):
        temp = key_words[i - 1][:]
        if i % 4 == 0:
            temp = temp[1:] + temp[:1]
            temp = [SBOX[b] for b in temp]
            temp[0] ^= RCON[i // 4]
        word = [key_words[i - 4][j] ^ temp[j] for j in range(4)]
        key_words.append(word)

    round_keys = []
    for r in range(num_rounds + 1):
        round_key = []
        for w in key_words[4 * r : 4 * r + 4]:
            round_key.extend(w)
        round_keys.append(round_key)

    return round_keys
