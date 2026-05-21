<div align="center">

# 🔐 CYBORG

### Encrypted Image Steganography using Deep Learning

[![Live Demo](https://img.shields.io/badge/Live-Demo-00e5ff?style=for-the-badge&logo=vercel&logoColor=white)](https://cyborg-frontend-one.vercel.app)
[![API](https://img.shields.io/badge/API-HuggingFace-yellow?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/spaces/StrawHat7/cyborg)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](#)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](#)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#license)

<br/>

**Cyborg** is a multi-layer encrypted image steganography platform that hides secret messages inside natural images using a trained deep neural network (StegoGAN), secured by a 5-layer cryptographic pipeline.

<br/>

<img src="docs/architecture.png" alt="Cyborg Architecture" width="700"/>

</div>

---

## ✨ Features

- **🧠 Deep Learning Steganography** — StegoGAN (HiDDeN-based U-Net encoder + decoder) trained on 42K animal images for invisible message embedding
- **🔒 5-Layer Security Pipeline** — AES-256-GCM → Lookup Table → XOR+PBKDF2 → StegoGAN → LSB Scrambling
- **📊 High Fidelity** — PSNR ~26 dB, SSIM ~0.95 with 60-bit message capacity
- **🌐 Full-Stack Web App** — React frontend + FastAPI backend, deployed and accessible online
- **📤 User Image Upload** — Encode messages into your own images or choose from a gallery
- **🔄 Circular Buffer** — 55-entry FIFO lookup table with automatic eviction (slots 1–63)

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────────────┐
                        │           CYBORG PIPELINE               │
                        └─────────────────────────────────────────┘

  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐    ┌───────────┐
  │  AES-256 │ →  │ Lookup Table │ →  │  XOR+PBKDF2  │ →  │ StegoGAN │ →  │    LSB    │
  │  GCM     │    │ (Circular)   │    │  (100K iter) │    │  (E464)  │    │ Scramble  │
  └──────────┘    └──────────────┘    └──────────────┘    └──────────┘    └───────────┘
   Message →        Ciphertext →        6-bit ref →        60-bit ECC →     Stego PNG
   Ciphertext       6-digit ref         Encrypted bits     Stego image      (final)
```

### Security Layers

| Layer | Method | Purpose |
|-------|--------|---------|
| **1** | AES-256-GCM | Encrypts the plaintext message with authenticated encryption |
| **2** | Lookup Table | Maps ciphertext → 6-digit reference number (000001–000063) |
| **3** | XOR + PBKDF2 | Encrypts the 6-bit ref with PIN-derived key (100K iterations) |
| **4** | StegoGAN | Embeds 60 bits (6-bit × 10× ECC) into cover image via neural network |
| **5** | LSB Scrambling | Reversible PIN-seeded noise on least significant bits |

---

## 🧬 Model Details

| Metric | Value |
|--------|-------|
| Architecture | HiDDeN v9.1 (U-Net + SE Attention + 4-scale injection) |
| Encoder (G) | 11.2M parameters |
| Decoder (R) | 12.9M parameters |
| Message Capacity | 60 bits (6 payload × 10× ECC repetition) |
| Training Data | 42,309 images (animals10 + animal-faces) |
| Checkpoint | Epoch 464 (ckpt_e464.pth) |
| Delta Scale | δ = 0.38 |
| PSNR | ~26 dB (avg over 200 test images) |
| SSIM | ~0.95 |
| Bit Accuracy | ~86.3% raw → ~96% after 10× majority-vote ECC |

---

## 📂 Project Structure

```
cyborg/
├── backend/                  # FastAPI + PyTorch backend
│   ├── app.py                # API endpoints (/encode, /decode, /images)
│   ├── model.py              # EncoderG (U-Net) + DecoderR architecture
│   ├── crypto.py             # AES-256-GCM encryption/decryption
│   ├── encryption.py         # XOR + PBKDF2 bit-level encryption
│   ├── decryption.py         # XOR + PBKDF2 bit-level decryption
│   ├── ecc.py                # 10× repetition error-correcting code
│   ├── lookup_table.py       # Circular buffer lookup table (cap: 55)
│   ├── lsb.py                # Reversible LSB scrambling layer
│   ├── pipeline_sender.py    # End-to-end encoding pipeline
│   ├── pipeline_receiver.py  # End-to-end decoding pipeline
│   ├── Dockerfile            # HuggingFace Spaces deployment
│   └── ckpt_e464.pth         # Trained model checkpoint (339MB)
│
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── api/client.js     # API client (encode, decode, gallery)
│   │   ├── components/       # ImageGallery, InputFields, ResultView
│   │   ├── pages/            # LandingPage, EncodePage, DecodePage
│   │   └── utils/            # Validation, constants
│   └── vercel.json           # Vercel deployment config
│
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PyTorch 2.x
- Model checkpoint `ckpt_e464.pth` (placed in `backend/`)

### Backend

```bash
cd backend
pip install -r requirements.txt
pip install torch torchvision
python -m uvicorn app:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and connects to the backend at `http://localhost:8000`.

---

## 🌐 Deployment

| Component | Platform | URL |
|-----------|----------|-----|
| **Frontend** | Vercel | [cyborg-frontend-one.vercel.app](https://cyborg-frontend-one.vercel.app) |
| **Backend** | HuggingFace Spaces (Docker) | [strawhat7-cyborg.hf.space](https://strawhat7-cyborg.hf.space) |

---

## 🔧 API Reference

### `POST /encode`

Hide a message inside an image.

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_url` | string (optional) | URL of cover image from gallery |
| `image_file` | file (optional) | Uploaded cover image |
| `message` | string | Secret message to hide |
| `pin` | string | Shared PIN for encryption |
| `salt` | string | Shared salt for key derivation |

**Response:** PNG image stream with `X-Ref-Number` header.

### `POST /decode`

Extract a hidden message from a stego image.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file` | file | Stego image (PNG) |
| `pin` | string | Shared PIN |
| `salt` | string | Shared salt |

**Response:** `{ "ref_number": "000011", "message": "decoded text" }`

### `GET /images`

Returns random cover images from HuggingFace dataset.

### `GET /health`

Health check endpoint.

---

## 📊 Performance Benchmarks

| Metric | Cyborg (Ours) | HiDDeN | Stable Signature |
|--------|:------------:|:------:|:----------------:|
| Bit Accuracy (raw) | 86.3% | 95.0% | 90.0% |
| Bit Accuracy (ECC) | ~96% | — | — |
| PSNR (dB) | 25.9 | 33.0+ | 38.0+ |
| SSIM | 0.952 | 0.97+ | 0.98+ |
| Security Layers | **5** | 0 | 0 |
| Message Capacity | 60 bits | 30 bits | 48 bits |

> **Note:** Cyborg trades some PSNR for a 5-layer security pipeline. Pure steganographic systems (HiDDeN, Stable Signature) have no encryption — the embedded bits are plaintext.

---

## 🛡️ Security Design

- **Key Independence:** AES and XOR layers use domain-separated PBKDF2 salts (`cyborg-aes:` / `cyborg-xor:` / `cyborg-lsb:`) ensuring cryptographic separation
- **No Plaintext in Channel:** The message never travels through the steganographic channel — only a 6-bit encrypted reference
- **Forward Secrecy of Table:** Circular eviction ensures old entries are automatically purged
- **PIN + Salt:** Both are required for every operation — knowing one without the other is insufficient

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with 🧠 by [Sujoy Maity](https://github.com/sujoy146)**

</div>
