"""AES-128 block cipher with CBC mode."""

from __future__ import annotations

import os
from typing import List

from aes.addroundkey import add_round_key
from aes.key_expansion import expand_key
from aes.mixcolumns import inv_mix_columns, mix_columns
from aes.shiftrows import inv_shift_rows, shift_rows
from aes.subbytes import inv_sub_bytes, sub_bytes


class AES:
    BLOCK_SIZE = 16
    KEY_SIZE = 16
    NUM_ROUNDS = 10

    def __init__(self, key: bytes):
        if len(key) != self.KEY_SIZE:
            raise ValueError("AES-128 requires a 16-byte key")
        self.round_keys = expand_key(key, self.NUM_ROUNDS)

    @staticmethod
    def generate_key() -> bytes:
        return os.urandom(AES.KEY_SIZE)

    def encrypt_block(self, block: bytes) -> bytes:
        if len(block) != self.BLOCK_SIZE:
            raise ValueError("Block must be exactly 16 bytes")

        state = list(block)
        add_round_key(state, self.round_keys[0])

        for rnd in range(1, self.NUM_ROUNDS):
            sub_bytes(state)
            shift_rows(state)
            mix_columns(state)
            add_round_key(state, self.round_keys[rnd])

        sub_bytes(state)
        shift_rows(state)
        add_round_key(state, self.round_keys[self.NUM_ROUNDS])

        return bytes(state)

    def decrypt_block(self, block: bytes) -> bytes:
        if len(block) != self.BLOCK_SIZE:
            raise ValueError("Block must be exactly 16 bytes")

        state = list(block)
        add_round_key(state, self.round_keys[self.NUM_ROUNDS])

        for rnd in range(self.NUM_ROUNDS - 1, 0, -1):
            inv_shift_rows(state)
            inv_sub_bytes(state)
            add_round_key(state, self.round_keys[rnd])
            inv_mix_columns(state)

        inv_shift_rows(state)
        inv_sub_bytes(state)
        add_round_key(state, self.round_keys[0])

        return bytes(state)

    @staticmethod
    def _pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
        pad_len = block_size - (len(data) % block_size)
        return data + bytes([pad_len] * pad_len)

    @staticmethod
    def _pkcs7_unpad(data: bytes) -> bytes:
        if not data:
            raise ValueError("Cannot unpad empty data")
        pad_len = data[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError("Invalid PKCS7 padding")
        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("Invalid PKCS7 padding bytes")
        return data[:-pad_len]

    def encrypt_cbc(self, plaintext: bytes, iv: bytes | None = None) -> tuple[bytes, bytes]:
        if iv is None:
            iv = os.urandom(self.BLOCK_SIZE)
        if len(iv) != self.BLOCK_SIZE:
            raise ValueError("IV must be 16 bytes")

        padded = self._pkcs7_pad(plaintext)
        ciphertext = bytearray()
        prev = iv

        for i in range(0, len(padded), self.BLOCK_SIZE):
            block = padded[i : i + self.BLOCK_SIZE]
            xored = bytes(a ^ b for a, b in zip(block, prev))
            encrypted = self.encrypt_block(xored)
            ciphertext.extend(encrypted)
            prev = encrypted

        return iv, bytes(ciphertext)

    def decrypt_cbc(self, ciphertext: bytes, iv: bytes) -> bytes:
        if len(iv) != self.BLOCK_SIZE:
            raise ValueError("IV must be 16 bytes")
        if len(ciphertext) % self.BLOCK_SIZE != 0:
            raise ValueError("Ciphertext length must be a multiple of 16")

        plaintext = bytearray()
        prev = iv

        for i in range(0, len(ciphertext), self.BLOCK_SIZE):
            block = ciphertext[i : i + self.BLOCK_SIZE]
            decrypted = self.decrypt_block(block)
            plaintext.extend(bytes(a ^ b for a, b in zip(decrypted, prev)))
            prev = block

        return self._pkcs7_unpad(bytes(plaintext))
