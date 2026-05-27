# Technical Report
## Secure Exam Submission System — RSA & AES Hybrid Cryptosystem

---

**Course:** Data Security / Cryptography Project  
**Project Title:** Secure Exam Submission System  
**Implementation Language:** Python 3.10+  
**Date:** May 2026  

---

### Cover Page Links *(fill before submission)*

| Item | Link |
|------|------|
| **Public GitHub Repository** | `[INSERT PUBLIC GITHUB URL HERE]` |
| **Demonstration Video (Google Drive)** | `[INSERT PUBLIC DRIVE URL HERE]` |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Model](#2-business-model)
3. [System Architecture](#3-system-architecture)
4. [RSA Implementation](#4-rsa-implementation)
5. [AES Implementation](#5-aes-implementation)
6. [Hybrid Cryptosystem Workflow](#6-hybrid-cryptosystem-workflow)
7. [Encoding Scheme](#7-encoding-scheme)
8. [Algorithms Summary](#8-algorithms-summary)
9. [Key Generation Process](#9-key-generation-process)
10. [User Interface](#10-user-interface)
11. [Project Structure](#11-project-structure)
12. [Testing and Verification](#12-testing-and-verification)
13. [Team Contributions](#13-team-contributions)
14. [AI Usage Disclosure](#14-ai-usage-disclosure)
15. [References](#15-references)

---

## 1. Executive Summary

This project implements a **hybrid cryptosystem** combining **RSA** (asymmetric encryption) and **AES-128** (symmetric encryption) from scratch, without using external cryptographic libraries. The system is demonstrated through a **Secure Exam Submission System** where students encrypt exam files using AES, protect the AES session key with the instructor's RSA public key, and only the instructor—with the private key—can decrypt submissions.

All cryptographic primitives were implemented manually, including prime generation, modular exponentiation, AES round functions, and key expansion.

---

## 2. Business Model

### 2.1 Scenario: Secure Exam Submission System

Universities need to ensure exam submissions remain confidential during transfer and storage. Students must submit answers without exposing plaintext to unauthorized parties. Only the instructor should be able to read submissions.

### 2.2 Roles and Workflow

| Role | Responsibility |
|------|----------------|
| **Instructor** | Generates RSA key pair; distributes **public key**; keeps **private key** secret |
| **Student** | Encrypts exam file/text; submits encrypted `.submission` package |
| **Instructor** | Decrypts submissions using private key |

### 2.3 Why Hybrid Encryption?

| Algorithm | Strength | Limitation |
|-----------|----------|------------|
| **RSA** | Secure key exchange | Slow; limited message size |
| **AES** | Fast bulk encryption | Requires shared secret key |

**Solution:** AES encrypts the exam (large data). RSA encrypts only the 16-byte AES session key (small data). This is the industry-standard hybrid approach used in TLS and secure messaging.

### 2.4 Real-World Use Case

1. Instructor publishes public key at course start.
2. Student completes exam offline, encrypts with hybrid system.
3. Encrypted package uploaded to LMS (Learning Management System).
4. Instructor decrypts locally with private key—plaintext never stored on server.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        STUDENT (Sender)                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Load exam file / type message (UTF-8)                        │
│  2. Generate random AES-128 session key                          │
│  3. AES-CBC encrypt exam → ciphertext + IV                       │
│  4. RSA encrypt AES key with instructor PUBLIC key               │
│  5. Save EncryptedPackage (.submission JSON, Base64 fields)      │
└────────────────────────────┬────────────────────────────────────┘
                             │ Encrypted package
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INSTRUCTOR (Receiver)                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Load .submission file                                        │
│  2. RSA decrypt AES key with PRIVATE key                         │
│  3. AES-CBC decrypt ciphertext → original exam                   │
│  4. View / save decrypted file                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Module Structure

```
SecureExamSystem/
├── rsa/          → Prime gen, GCD, modexp, RSA encrypt/decrypt
├── aes/          → SubBytes, ShiftRows, MixColumns, AddRoundKey, CBC
├── hybrid/       → Combines RSA + AES workflow
├── ui/           → Tkinter desktop application
└── main.py       → Entry point
```

---

## 4. RSA Implementation

**Location:** `rsa/` module (files: `prime_generation.py`, `gcd.py`, `mod_inverse.py`, `mod_exp.py`, `rsa_main.py`)

### 4.1 Prime Generation

We use the **Miller-Rabin** probabilistic primality test with 20 rounds. Random odd candidates of the required bit length are generated until a probable prime is found.

```
generate_prime(bits) → probable prime p or q
```

### 4.2 Key Mathematics

| Function | File | Purpose |
|----------|------|---------|
| `gcd(a, b)` | `gcd.py` | Euclidean algorithm |
| `extended_gcd(a, b)` | `gcd.py` | Returns (g, x, y) where ax + by = g |
| `mod_inverse(a, m)` | `mod_inverse.py` | Computes d such that e·d ≡ 1 (mod φ(n)) |
| `mod_exp(base, exp, mod)` | `mod_exp.py` | Square-and-multiply; **pow() is NOT used** |

### 4.3 Key Generation

For RSA-2048:
1. Generate two primes p, q (1024 bits each)
2. Compute n = p × q
3. Compute φ(n) = (p−1)(q−1)
4. Choose public exponent e = 65537
5. Verify gcd(e, φ(n)) = 1
6. Compute private exponent d = e⁻¹ mod φ(n)

**Public key:** (n, e)  
**Private key:** (n, d)

### 4.4 Encryption and Decryption

Messages use **PKCS#1 v1.5** padding before encryption.

```
Encryption:  C = M^e mod n    (using mod_exp)
Decryption:  M = C^d mod n    (using mod_exp)
```

In our hybrid system, RSA encrypts only the **16-byte AES session key**, which fits within the RSA block size.

### 4.5 Compliance

- No `cryptography`, `pycrypto`, OpenSSL, or built-in RSA APIs
- No `pow(a, b, m)` in production code
- All arithmetic implemented manually

---

## 5. AES Implementation

**Location:** `aes/` module (AES-128, CBC mode)

### 5.1 Parameters

| Parameter | Value |
|-----------|-------|
| Key size | 128 bits (16 bytes) |
| Block size | 128 bits (16 bytes) |
| Rounds | 10 |
| Mode | CBC with PKCS7 padding |

### 5.2 Round Functions (Separate Files)

| Transformation | File | Description |
|----------------|------|-------------|
| **SubBytes** | `subbytes.py` | S-box substitution on each byte |
| **ShiftRows** | `shiftrows.py` | Cyclic row shifts of 4×4 state |
| **MixColumns** | `mixcolumns.py` | Column mixing in GF(2⁸) |
| **AddRoundKey** | `addroundkey.py` | XOR state with round key |
| **Key Expansion** | `key_expansion.py` | Expand 128-bit key to 11 round keys |

### 5.3 Encryption Round Structure

```
Initial:     AddRoundKey(K₀)

Rounds 1–9:  SubBytes → ShiftRows → MixColumns → AddRoundKey

Final (10):  SubBytes → ShiftRows → AddRoundKey   (no MixColumns)
```

Decryption applies inverse transformations in reverse order.

### 5.4 CBC Mode

For multi-block messages (exam files):
1. Generate random 16-byte IV
2. PKCS7-pad plaintext to multiple of 16 bytes
3. For each block: XOR with previous ciphertext (or IV) → AES encrypt block
4. Store IV + ciphertext

### 5.5 Verification

Implementation verified against standard AES-128 test vector (FIPS-197 / OpenSSL reference).

---

## 6. Hybrid Cryptosystem Workflow

**Location:** `hybrid/hybrid_system.py`

### 6.1 Encryption (Student Side)

```
Step 1:  aes_key ← AES.generate_key()           // 16 random bytes
Step 2:  (iv, ciphertext) ← AES.encrypt_cbc(exam_data)
Step 3:  enc_key ← RSA.encrypt(aes_key)         // instructor public key
Step 4:  Package → JSON with Base64-encoded fields
```

### 6.2 Decryption (Instructor Side)

```
Step 1:  enc_key, iv, ciphertext ← load from package (Base64 decode)
Step 2:  aes_key ← RSA.decrypt(enc_key)         // instructor private key
Step 3:  exam_data ← AES.decrypt_cbc(ciphertext, iv)
```

### 6.3 Encrypted Package Format

```json
{
  "student_id": "STU-001",
  "filename": "exam.pdf",
  "encrypted_aes_key_b64": "<RSA-encrypted key, Base64>",
  "iv_b64": "<16-byte IV, Base64>",
  "ciphertext_b64": "<AES ciphertext, Base64>"
}
```

### 6.4 Security Properties

- Each submission uses a **unique AES session key**
- Without private key, AES key cannot be recovered
- Without AES key, exam content cannot be decrypted
- Encrypted package stored as text-safe JSON

---

## 7. Encoding Scheme

### 7.1 Schemes Used

| Encoding | Purpose | Where Used |
|----------|---------|------------|
| **UTF-8** | Text representation | Exam answers, UI input/output, JSON metadata |
| **Base64** | Binary → ASCII text | `encrypted_aes_key_b64`, `iv_b64`, `ciphertext_b64` in `.submission` |
| **Hexadecimal** | Debug/display | Crypto Demo tab, console output |

### 7.2 Why UTF-8?

Exam answers may contain English, Arabic, or symbols. UTF-8 is the universal standard for converting human-readable text to bytes before AES encryption.

### 7.3 Why Base64?

Encrypted output is **binary data** (random bytes). JSON and text files cannot safely store raw binary. Base64 converts every 3 bytes into 4 printable ASCII characters, making the encrypted package storable and transferable.

**Example:**
```
Binary:  69 c4 e0 d8 6a 7b ...
Base64:  "acTg2Gp7BDMA..."
```

### 7.4 Why Hexadecimal?

Used in the Crypto Demo tab for human-readable display of keys and ciphertext during demonstrations. Each byte = 2 hex digits (e.g., `0x69` → `"69"`).

### 7.5 Conversion Pipeline

```
[Send]    Text (UTF-8) → bytes → AES encrypt → binary → Base64 → JSON file
[Receive] JSON file → Base64 decode → binary → AES decrypt → bytes → Text (UTF-8)
```

**Note:** Python's `base64` module is used for **encoding only**, not cryptography. This is permitted by project rules.

---

## 8. Algorithms Summary

| Algorithm | Type | Implementation |
|-----------|------|----------------|
| Miller-Rabin | Primality test | `rsa/prime_generation.py` |
| Euclidean GCD | Integer math | `rsa/gcd.py` |
| Extended Euclidean | Modular inverse | `rsa/gcd.py`, `rsa/mod_inverse.py` |
| Square-and-Multiply | Modular exponentiation | `rsa/mod_exp.py` |
| RSA | Asymmetric cipher | `rsa/rsa_main.py` |
| AES-128 | Block cipher | `aes/aes_main.py` |
| CBC + PKCS7 | Block mode / padding | `aes/aes_main.py` |
| Hybrid wrap | Key encapsulation | `hybrid/hybrid_system.py` |

---

## 9. Key Generation Process

### 9.1 RSA Key Generation (One-Time, Instructor)

1. Run UI → **Generate RSA Key Pair (2048-bit)**
2. System generates p, q via Miller-Rabin
3. Computes n, e, d
4. Saves `instructor_public.json` and `instructor_private.json`

### 9.2 AES Session Key (Per Submission)

1. Generated fresh for each encrypt operation
2. 16 cryptographically random bytes via `os.urandom(16)`
3. Never stored in plaintext—only RSA-encrypted form in package

---

## 10. User Interface

**Technology:** Python Tkinter (desktop application)  
**Location:** `ui/app.py`

### 10.1 Workflow Tabs

| Section | Function |
|---------|----------|
| **1. Generate RSA Keys** | Instructor creates/loads key pair |
| **2. Enter Message / File** | Student types text or loads exam file |
| **3. Encrypt** | Hybrid encryption |
| **4. Encrypted AES Key** | Displays RSA-encrypted session key (Base64) |
| **5. Encrypted Data** | Displays IV and ciphertext (Base64) |
| **6. Decrypt** | Instructor decrypts package |
| **7. Original Message** | Shows recovered exam content |

### 10.2 UI Screenshots

*(Insert screenshots before final submission)*

**Figure 1:** Main window — Hybrid Workflow tab  
![Figure 1: Main UI](screenshots/01_main_ui.png)

**Figure 2:** RSA key generation  
![Figure 2: Key Generation](screenshots/02_key_generation.png)

**Figure 3:** Message input and file load  
![Figure 3: Message Input](screenshots/03_message_input.png)

**Figure 4:** Encrypted AES key and encrypted data displayed  
![Figure 4: Encrypted Output](screenshots/04_encrypted_output.png)

**Figure 5:** Decrypted original message  
![Figure 5: Decrypted Message](screenshots/05_decrypted_message.png)

**Figure 6:** Crypto Demo tab  
![Figure 6: Crypto Demo](screenshots/06_crypto_demo.png)

> **Instructions:** Run `py main.py`, capture screenshots, save to `docs/screenshots/`, re-export PDF.

### 10.3 How to Run

```bash
cd SecureExamSystem
py main.py              # GUI
py main.py --mode demo  # Console demo
```

---

## 11. Project Structure

```
SecureExamSystem/
├── rsa/
│   ├── prime_generation.py
│   ├── gcd.py
│   ├── mod_inverse.py
│   ├── mod_exp.py
│   └── rsa_main.py
├── aes/
│   ├── subbytes.py
│   ├── shiftrows.py
│   ├── mixcolumns.py
│   ├── addroundkey.py
│   ├── key_expansion.py
│   └── aes_main.py
├── hybrid/
│   └── hybrid_system.py
├── ui/
│   └── app.py
├── main.py
└── README.md
```

---

## 12. Testing and Verification

### 12.1 Final Submission Test Scenario

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Generate RSA-2048 keys | Keys saved to `keys/` |
| 2 | Load `exam.pdf` | File loaded in UI |
| 3 | Encrypt | Sections 4 & 5 show Base64 ciphertext |
| 4 | Save `.submission` | File in `submissions/` |
| 5 | Decrypt with private key | Section 7 shows original content |
| 6 | Compare files | Decrypted file identical to original |

### 12.2 Cryptographic Verification

- AES-128 matches standard test vector
- RSA encrypt/decrypt roundtrip verified
- Hybrid full workflow verified
- No forbidden libraries detected in codebase

---

## 13. Team Contributions

*(Fill in with actual group member names before submission)*

| Member | Name | Contribution |
|--------|------|--------------|
| Member 1 | `[NAME]` | RSA module: prime generation, GCD, extended Euclidean, modular inverse, modular exponentiation, key generation |
| Member 2 | `[NAME]` | AES module: SubBytes, ShiftRows, MixColumns, AddRoundKey, key expansion, CBC mode |
| Member 3 | `[NAME]` | Hybrid layer, encoding scheme (UTF-8, Base64, Hex), package format |
| Member 4 | `[NAME]` | UI development, business model integration, testing |
| Member 5 | `[NAME]` | Technical report, README, GitHub setup, demonstration video |

---

## 14. AI Usage Disclosure

*(Required — edit honestly before submission)*

### 14.1 Where AI Was Used

| Area | AI Assistance |
|------|---------------|
| Initial project structure | AI suggested folder layout and module separation |
| AES S-box tables | AI provided standard FIPS-197 lookup tables for verification |
| README and report drafting | AI helped draft documentation structure |
| Debugging | AI assisted in fixing inverse ShiftRows in AES decryption |

### 14.2 Why AI Was Used

- To accelerate initial implementation scaffolding
- To verify algorithm structure against published standards (FIPS-197, PKCS#1)
- To draft documentation templates

### 14.3 What Was Modified by the Team

- All cryptographic logic was reviewed and understood by team members
- RSA modular exponentiation implemented manually (square-and-multiply)
- AES round functions implemented and tested independently
- UI workflow customized for Secure Exam Submission scenario
- Team contributions and testing performed manually

### 14.4 Team Understanding

Each member can explain:
- How Miller-Rabin prime generation works
- Why hybrid encryption uses RSA for keys and AES for data
- The AES round structure (SubBytes, ShiftRows, MixColumns, AddRoundKey)
- How Base64 encoding enables JSON storage of binary ciphertext
- The complete encrypt/decrypt workflow in the UI

---

## 15. References

1. NIST FIPS 197 — *Advanced Encryption Standard (AES)*, 2001.  
   https://csrc.nist.gov/publications/detail/fips/197/final

2. PKCS #1 v1.5 — *RSA Encryption Standard*, RSA Laboratories.

3. Stallings, W. — *Cryptography and Network Security* (RSA, AES chapters).

4. Course lecture notes — Data Security / Cryptography lectures.

5. Miller, G. L. — *Riemann's Hypothesis and Tests for Primality*, 1976 (Miller-Rabin basis).

6. Rabin, M. O. — *Probabilistic Algorithm for Testing Primality*, 1980.

---

## Appendix A: Example Input / Output

### Input (Plaintext)
```
Student ID: STU-001
Message: "Answer Q1: Hybrid encryption uses RSA for the AES key."
```

### Output (Encrypted Package — excerpt)
```json
{
  "student_id": "STU-001",
  "filename": "STU-001_message.txt",
  "encrypted_aes_key_b64": "aGVsbG8... (256+ chars)",
  "iv_b64": "xK3m9pL2... (24 chars)",
  "ciphertext_b64": "7FpQx2... (variable length)"
}
```

### Output (After Decryption)
```
Answer Q1: Hybrid encryption uses RSA for the AES key.
```

---

**End of Technical Report**
