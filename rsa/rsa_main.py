"""RSA key generation, encryption, and decryption."""

from __future__ import annotations

import json
import os
import random
from typing import Tuple

from rsa.gcd import gcd
from rsa.mod_exp import mod_exp
from rsa.mod_inverse import mod_inverse
from rsa.prime_generation import generate_prime


def bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big")


def int_to_bytes(value: int, length: int) -> bytes:
    return value.to_bytes(length, byteorder="big")


class RSA:
    DEFAULT_E = 65537

    def __init__(self, n: int | None = None, e: int | None = None, d: int | None = None):
        self.n = n
        self.e = e
        self.d = d

    @classmethod
    def generate_keys(cls, bits: int = 2048) -> "RSA":
        if bits < 512:
            raise ValueError("RSA key size must be at least 512 bits")

        half = bits // 2
        while True:
            p = generate_prime(half)
            q = generate_prime(half)
            if p == q:
                continue

            n = p * q
            phi = (p - 1) * (q - 1)
            e = cls.DEFAULT_E

            if gcd(e, phi) != 1:
                continue

            d = mod_inverse(e, phi)
            return cls(n=n, e=e, d=d)

    @property
    def public_key(self) -> Tuple[int, int]:
        return self.n, self.e

    @property
    def private_key(self) -> Tuple[int, int]:
        return self.n, self.d

    def _max_message_bytes(self) -> int:
        if self.n is None:
            raise ValueError("RSA modulus is not set")
        k = (self.n.bit_length() + 7) // 8
        return k - 11

    def encrypt(self, plaintext: bytes) -> bytes:
        if self.n is None or self.e is None:
            raise ValueError("Public key is not set")

        max_len = self._max_message_bytes()
        if len(plaintext) > max_len:
            raise ValueError(f"Plaintext too long for RSA key ({len(plaintext)} > {max_len} bytes)")

        k = (self.n.bit_length() + 7) // 8
        padded = self._pkcs1_v15_encode(plaintext, k)
        m = bytes_to_int(padded)
        c = mod_exp(m, self.e, self.n)
        return int_to_bytes(c, k)

    def decrypt(self, ciphertext: bytes) -> bytes:
        if self.n is None or self.d is None:
            raise ValueError("Private key is not set")

        k = (self.n.bit_length() + 7) // 8
        if len(ciphertext) != k:
            raise ValueError("Invalid ciphertext length")

        c = bytes_to_int(ciphertext)
        m = mod_exp(c, self.d, self.n)
        padded = int_to_bytes(m, k)
        return self._pkcs1_v15_decode(padded)

    @staticmethod
    def _pkcs1_v15_encode(message: bytes, k: int) -> bytes:
        if len(message) > k - 11:
            raise ValueError("Message too long for PKCS#1 v1.5 encoding")

        padding_len = k - len(message) - 3
        padding = bytes([0x00, 0x02])
        padding += bytes(random.randint(1, 255) for _ in range(padding_len))
        padding += b"\x00"
        return padding + message

    @staticmethod
    def _pkcs1_v15_decode(block: bytes) -> bytes:
        if len(block) < 11 or block[0] != 0x00 or block[1] != 0x02:
            raise ValueError("Invalid PKCS#1 v1.5 block header")

        try:
            sep = block.index(0x00, 2)
        except ValueError as exc:
            raise ValueError("Invalid PKCS#1 v1.5 padding") from exc

        if sep < 10:
            raise ValueError("Invalid PKCS#1 v1.5 padding length")

        return block[sep + 1 :]

    def save_public_key(self, path: str) -> None:
        data = {"n": str(self.n), "e": str(self.e)}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_private_key(self, path: str) -> None:
        data = {"n": str(self.n), "e": str(self.e), "d": str(self.d)}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_public_key(cls, path: str) -> "RSA":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(n=int(data["n"]), e=int(data["e"]))

    @classmethod
    def load_private_key(cls, path: str) -> "RSA":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(n=int(data["n"]), e=int(data["e"]), d=int(data["d"]))

    @staticmethod
    def generate_random_bytes(length: int) -> bytes:
        return os.urandom(length)
