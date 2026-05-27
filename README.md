# SecureExamSystem

**A hybrid RSA + AES cryptosystem for secure exam submission — implemented from scratch in Python.**

SecureExamSystem is an academic Data Security / Cryptography project that demonstrates industry-standard **hybrid encryption**: AES encrypts exam content (fast, bulk data), and RSA encrypts only the AES session key (secure key exchange). All cryptographic primitives are implemented manually without external crypto libraries.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Cryptographic Design](#cryptographic-design)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation & Running](#installation--running)
- [User Guide](#user-guide)
- [Desktop Application](#desktop-application)
- [Submission Package Format](#submission-package-format)
- [Encoding Scheme](#encoding-scheme)
- [Implementation Compliance](#implementation-compliance)
- [Console Demo Mode](#console-demo-mode)
- [Runtime Directories](#runtime-directories)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Academic Context](#academic-context)

---

## Overview

Universities need exam submissions to remain confidential in transit and storage. This system models a realistic workflow:

| Role | Responsibility |
|------|----------------|
| **Instructor** | Generates an RSA key pair, shares the **public key**, keeps the **private key** secret, and decrypts student submissions |
| **Student** | Encrypts exam files or text using the instructor's **public key only** — cannot decrypt submissions |

The hybrid approach mirrors real-world protocols (e.g. TLS): symmetric encryption for performance, asymmetric encryption for key protection.

---

## Key Features

- **RSA-2048** — Miller–Rabin primality testing, extended Euclidean inverse, square-and-multiply modular exponentiation, PKCS#1 v1.5 padding
- **AES-128** — Full 10-round cipher with separate transform modules, CBC mode, PKCS#7 padding
- **Hybrid layer** — Combines RSA and AES into a complete encrypt/decrypt workflow
- **Desktop GUI** — Separate Instructor and Student portals, built-in instructions, crypto demos, scrollable tabs
- **Submission packages** — Portable `.submission` JSON files with Base64-encoded ciphertext fields
- **No external crypto libraries** — All primitives implemented from first principles

---

## Cryptographic Design

### Why Hybrid Encryption?

| Algorithm | Strength | Limitation |
|-----------|----------|------------|
| **RSA** | Secure asymmetric key exchange | Slow; limited plaintext size per block |
| **AES** | Fast symmetric bulk encryption | Requires a shared secret key |

**Solution:** Generate a random AES session key per submission. AES encrypts the exam; RSA encrypts only the 16-byte AES key using the instructor's public key.

### RSA Module (`rsa/`)

| Component | File | Description |
|-----------|------|-------------|
| Prime generation | `prime_generation.py` | Random odd candidates + Miller–Rabin primality test |
| GCD | `gcd.py` | Euclidean algorithm |
| Modular inverse | `mod_inverse.py` | Extended Euclidean algorithm |
| Modular exponentiation | `mod_exp.py` | Square-and-multiply (no built-in `pow()` for crypto) |
| RSA core | `rsa_main.py` | Key generation, PKCS#1 v1.5 encrypt/decrypt, JSON key I/O |

- **Key size:** 2048 bits (default in GUI)
- **Public exponent:** e = 65537
- **Padding:** PKCS#1 v1.5 (encryption block type 0x02)

### AES Module (`aes/`)

| Transform | File |
|-----------|------|
| SubBytes | `subbytes.py` |
| ShiftRows | `shiftrows.py` |
| MixColumns | `mixcolumns.py` |
| AddRoundKey | `addroundkey.py` |
| Key expansion | `key_expansion.py` |
| Cipher + CBC | `aes_main.py` |

- **Variant:** AES-128 (16-byte key, 10 rounds, 16-byte blocks)
- **Mode:** CBC with random IV per encryption
- **Padding:** PKCS#7

### Hybrid Module (`hybrid/`)

`hybrid_system.py` orchestrates the full workflow:

1. Generate random AES-128 session key  
2. AES-CBC encrypt exam plaintext → ciphertext + IV  
3. RSA encrypt AES key with instructor **public** key  
4. Package fields into `EncryptedPackage` and save as `.submission`  

Decryption reverses the steps using the instructor **private** key.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        STUDENT (Sender)                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Load exam file or type message (UTF-8)                       │
│  2. Generate random AES-128 session key                          │
│  3. AES-CBC encrypt exam → ciphertext + IV                       │
│  4. RSA encrypt AES key with instructor PUBLIC key               │
│  5. Save EncryptedPackage (.submission JSON)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │  Encrypted .submission file
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INSTRUCTOR (Receiver)                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Load .submission file                                        │
│  2. RSA decrypt AES key with PRIVATE key                         │
│  3. AES-CBC decrypt ciphertext → original exam                    │
│  4. View or save decrypted file                                  │
└─────────────────────────────────────────────────────────────────┘
```

A detailed architecture diagram is available at:

`docs/diagrams/system_architecture.png` · `docs/diagrams/system_architecture.svg`

---

## Project Structure

```
SecureExamSystem/
├── rsa/
│   ├── prime_generation.py    # Miller–Rabin primes
│   ├── gcd.py                 # Greatest common divisor
│   ├── mod_inverse.py         # Extended Euclidean inverse
│   ├── mod_exp.py             # Modular exponentiation
│   └── rsa_main.py            # RSA keygen, encrypt, decrypt
├── aes/
│   ├── subbytes.py            # S-box substitution
│   ├── shiftrows.py           # Row shifts
│   ├── mixcolumns.py          # Column mixing (GF(2⁸))
│   ├── addroundkey.py         # Round key XOR
│   ├── key_expansion.py       # Key schedule
│   └── aes_main.py            # AES-128 + CBC mode
├── hybrid/
│   └── hybrid_system.py       # Hybrid encrypt/decrypt + package I/O
├── ui/
│   └── app.py                 # Tkinter desktop application
├── docs/
│   ├── Technical_Report.md    # Full technical report (Markdown)
│   └── diagrams/              # Architecture diagrams
├── keys/                      # RSA keys (created at runtime)
├── submissions/               # Encrypted student packages
├── decrypted/                 # Decrypted exam exports
├── main.py                    # Application entry point
└── README.md                  # This file
```

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **Python** | 3.10 or newer |
| **Standard library only** | `tkinter`, `json`, `base64`, `os`, `threading`, etc. |
| **OS** | Windows, macOS, or Linux |
| **Display** | GUI requires a desktop environment (Tkinter) |

No `pip install` is required — there are no third-party dependencies.

---

## Installation & Running

### Clone or download the project

```bash
cd SecureExamSystem
```

### Launch the graphical application (recommended)

```bash
py main.py
```

### Launch console demo (no GUI)

```bash
py main.py --mode demo
```

Runs automated checks for modular exponentiation, AES-CBC, RSA, and full hybrid workflow.

---

## User Guide

### Instructor workflow

| Step | Action |
|------|--------|
| 1 | Open **Instructor Portal** → **Generate RSA Key Pair (2048-bit)** |
| 2 | Wait 10–30 seconds. Keys save to `keys/instructor_public.json` and `keys/instructor_private.json` |
| 3 | Click **Copy Public Key for Students** and distribute `instructor_public.json` |
| 4 | **Never share** `instructor_private.json` |
| 5 | When a student sends a `.submission` file → **Browse** → **Load Submission** |
| 6 | Click **Decrypt Submission** → view content → **Save Decrypted Exam File** |

### Student workflow

| Step | Action |
|------|--------|
| 1 | Open **Student Portal** → load `instructor_public.json` → **Verify Key** |
| 2 | Enter **Student ID** (e.g. `STU-001`) |
| 3 | Type exam content or **Upload / Load Exam File** (PDF, TXT, PNG, etc.) |
| 4 | Click **Encrypt Submission** |
| 5 | Click **Send / Save Package** → file saved under `submissions/` |
| 6 | Send the `.submission` file to the instructor |

> **Important:** Students cannot decrypt submissions. Only the instructor holds the RSA private key.

### End-to-end test scenario

1. Instructor generates keys and shares the public key.  
2. Student encrypts `exam.txt` (or any file).  
3. Student delivers `STU-001_exam.txt.submission` to the instructor.  
4. Instructor loads, decrypts, and saves the original exam to `decrypted/`.

---

## Desktop Application

The GUI (`ui/app.py`) provides four tabs:

| Tab | Purpose |
|-----|---------|
| **Instructions** | Step-by-step guide for instructors and students |
| **Instructor Portal** | Key management, load submissions, decrypt, save exams |
| **Student Portal** | Load public key, prepare exam, encrypt, save package |
| **Crypto Demo** | Low-level AES block, RSA, and full hybrid tests |

Additional UI features:

- Scrollable tabs (mouse wheel + vertical scrollbar) for full page access  
- Activity log at the bottom of the window  
- Encrypted output preview (AES key, IV, ciphertext in Base64)  
- Background RSA key generation (non-blocking UI)

---

## Submission Package Format

Encrypted submissions are stored as JSON files with extension `.submission`:

```json
{
  "student_id": "STU-001",
  "filename": "exam.txt",
  "encrypted_aes_key_b64": "<RSA-encrypted AES key, Base64>",
  "iv_b64": "<AES-CBC initialization vector, Base64>",
  "ciphertext_b64": "<AES-encrypted exam content, Base64>"
}
```

**Filename pattern:** `{student_id}_{original_filename}.submission`  
**Example:** `STU-001_exam.txt.submission`

---

## Encoding Scheme

| Data type | Encoding | Usage |
|-----------|----------|-------|
| Text (exam content, UI) | **UTF-8** | Human-readable exam input/output |
| Binary fields in `.submission` | **Base64** | JSON-safe storage of keys, IV, ciphertext |
| Demo / debug display | **Hexadecimal** | Optional human-readable byte display |

---

## Implementation Compliance

This project was built to satisfy academic requirements for **manual cryptographic implementation**.

### Implemented from scratch

- Miller–Rabin primality testing  
- Modular exponentiation (square-and-multiply)  
- RSA key generation, PKCS#1 v1.5 encryption/decryption  
- Full AES-128 round functions and key expansion  
- AES-CBC with PKCS#7 padding  
- Hybrid encrypt/decrypt workflow  

### Permitted standard-library modules

`json`, `base64`, `os`, `random`, `tkinter`, `threading`, `dataclasses`, `argparse`

### Not used (prohibited for core crypto)

`cryptography`, `pycrypto`, `pycryptodome`, `PyOpenSSL`, `hashlib` (for cipher operations), `Cipher.AES`, or any library that provides ready-made RSA/AES primitives.

---

## Console Demo Mode

```bash
py main.py --mode demo
```

Expected output sections:

1. **mod_exp** — sanity check for modular exponentiation  
2. **AES CBC** — encrypt/decrypt round-trip match  
3. **RSA** — encrypt/decrypt round-trip match (1024-bit demo keys)  
4. **Hybrid** — full submission encrypt/decrypt match  

---

## Runtime Directories

These folders are created automatically when the application runs:

| Directory | Contents | Access |
|-----------|----------|--------|
| `keys/` | `instructor_public.json`, `instructor_private.json` | Instructor generates; students receive public key only |
| `submissions/` | Encrypted `.submission` files from students | Written by students; read by instructor |
| `decrypted/` | Exported plaintext exams after decryption | Instructor only |

> **Security note:** Do not commit private keys or real exam content to version control. Add `keys/`, `submissions/`, and `decrypted/` to `.gitignore` for public repositories.

---

## Documentation

| Document | Location |
|----------|----------|
| Technical Report (Markdown) | `docs/Technical_Report.md` |
| System architecture diagram | `docs/diagrams/system_architecture.png` · `system_architecture.svg` |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Public key not found** | Instructor must generate keys first, or student must set the correct path to `instructor_public.json` |
| **Decryption failed** | Wrong private key, corrupted `.submission` file, or submission encrypted with a different public key |
| **Student ID required** | Enter a Student ID before encrypting |
| **Key generation is slow** | Normal for RSA-2048; allow up to 30 seconds |
| **Cannot scroll in GUI** | Use the vertical scrollbar on the right of each tab, or the mouse wheel over the page background |
| **Tkinter not found (Linux)** | Install with `sudo apt install python3-tk` |

---

## Academic Context

| Item | Details |
|------|---------|
| **Course** | Data Security / Cryptography |
| **Project** | Secure Exam Submission System |
| **Language** | Python 3.10+ |
| **Paradigm** | Hybrid cryptosystem (RSA + AES) |

### Key ownership summary

| Key / Data | Who holds it | Purpose |
|------------|--------------|---------|
| RSA public key `(n, e)` | Instructor + all students | Encrypt AES session key |
| RSA private key `(n, d)` | Instructor only | Decrypt AES session key |
| AES session key | Generated per submission | Encrypt/decrypt exam content |
| `.submission` file | Student → Instructor | Stores all encrypted data |

---

## License & Usage

This project is submitted as an academic coursework artifact. Use and distribution should follow your institution's academic integrity policies. Replace placeholder links in the technical report (GitHub repository, demonstration video) before final submission.

---

**SecureExamSystem** — demonstrating secure hybrid encryption through a practical exam submission workflow.
