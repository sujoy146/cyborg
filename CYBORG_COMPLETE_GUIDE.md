# Cyborg — Complete Project Guide (Verified & Corrected)
**Project Title:** An Approach Towards Reversible Encrypted Image Steganography Using Machine Learning  
**Code Name:** Cyborg | **Model:** StegoGAN v9.1 (60-bit)  
**Author:** Sujoy Maity | **University:** MAKAUT, West Bengal  
**Last verified:** May 2026 (cross-checked against actual backend code)

---

## 1. What This Project Is

A **five-layer covert communication system** that hides an encrypted message inside an animal photograph. The stego image looks like a normal photo but carries a hidden reference token, recoverable only with the shared PIN and salt.

**The core innovation:** Unlike every other deep steganography system (HiDDeN, StegaStamp, DARI-Mark), Cyborg **never puts the actual secret inside the image**. Only a small encrypted lookup token travels through the neural channel. Even perfect extraction gives the attacker just a number 0-63 — useless without the server, PIN, and salt.

---

## 2. The Five-Layer Security Pipeline

```
Layer 1: AES-256-GCM     ->  Encrypt message, store ciphertext on server
Layer 2: Lookup Table     ->  Assign token t in {0..63} (6-bit, 64 entries max)
Layer 3: XOR + PBKDF2     ->  Encrypt token -> 6 encrypted bits
Layer 3b: 10x ECC         ->  Repeat each bit 10x -> 60 wire bits
Layer 4: StegoGAN G       ->  Embed 60 bits into 256x256 cover image
Layer 5: LSB Scrambling   ->  Deterministic LSB overwrite (anti-steganalysis)
```

### Domain-Separated Keys (Critical Security Feature)
All keys derive from the SAME (PIN, salt) pair with different prefixes:
- `cyborg-aes:` + salt -> AES-256 key (PBKDF2-HMAC-SHA256, 100k iterations, 256-bit)
- `cyborg-xor:` + salt -> XOR key (6 bits from first byte of PBKDF2 output)
- `cyborg-lsb:` + salt -> LSB scrambling seed (MD5 hash -> numpy RNG seed)

**Compromise of one key reveals nothing about the others.**

### Complete Sender/Receiver Flow
```
SENDER:
  message
    -> AES-256-GCM-Encrypt(message, PBKDF2(PIN, "cyborg-aes:" || salt))
    -> store ciphertext in server lookup table -> get token t (0-63)
    -> IntToBits(t, 6) -> XOR with PBKDF2-derived key bits -> 6 encrypted bits
    -> Repeat each bit 10x -> 60 wire bits
    -> StegoGAN G(cover_image, wire_bits, delta=0.38) -> stego image
    -> LSB-Scramble(stego, PBKDF2(PIN, "cyborg-lsb:" || salt))
    -> send stego image

RECEIVER:
    -> LSB-Unscramble(stego, same key)
    -> StegoGAN R(stego) -> 60 raw bits (sigmoid > 0.5)
    -> MajorityVote(bits, groups of 10) -> 6 ECC-decoded bits
    -> XOR with PBKDF2-derived key bits -> token t
    -> LookupTable.get(t) -> ciphertext
    -> AES-256-GCM-Decrypt(ciphertext, PBKDF2(PIN, "cyborg-aes:" || salt))
    -> original message
```

---

## 3. Architecture (StegoGAN v9.1)

### 3.1 EncoderG - U-Net with Multi-Scale Message Injection

**Input:** 256x256x3 cover image + 60-bit message vector  
**Output:** 256x256x3 stego image | **Base channels (ngf):** 64

```
ENCODER PATH:
  enc1: Conv(3->64)  @ 256x256  + msg_fc1(60->64)  injected via concat
  enc2: Conv(64->128, stride=2) @ 128x128 + msg_fc2(60->128) injected
  enc3: Conv(128->256, stride=2) @ 64x64  + msg_fc3(60->256) injected
  enc4: Conv(256->256, stride=2) @ 32x32  + msg_fc4(60->256) injected

BOTTLENECK (16x16):
  Conv(256->256, stride=2) -> ResBlock x3 -> SEBlock -> 256ch @ 16x16

DECODER PATH (with skip connections from encoder):
  dec4: Upsample(2x) + Conv -> concat(enc4 skip) -> 256ch @ 32x32
  dec3: Upsample(2x) + Conv -> concat(enc3 skip) -> 128ch @ 64x64
  dec2: Upsample(2x) + Conv -> concat(enc2 skip) -> 64ch  @ 128x128
  dec1: Upsample(2x) + Conv -> concat(enc1 skip) -> 32ch  @ 256x256
  out:  Conv(32->3, kernel=3) -> tanh

OUTPUT: stego = clamp(cover + delta * tanh(raw_output), -1, 1)
```

**Why multi-scale injection?** Distributes message across ALL spatial frequencies. HiDDeN injects only at bottleneck -> visible low-frequency artifacts.

**Why SE block?** Squeeze-and-Excitation learns channel-wise importance weights. Routes message bits to channels where perturbations are least perceptually detectable.

### 3.2 DecoderR - CNN + SE + Deep MLP

```
FEATURES:
  Conv(3->64, stride=2)    256->128
  Conv(64->128, stride=2)  128->64   + ResBlock
  Conv(128->256, stride=2) 64->32    + ResBlock
  Conv(256->512, stride=2) 32->16    + ResBlock
  Conv(512->512, stride=2) 16->8     + SEBlock
  Conv(512->512, stride=2) 8->4
  AdaptiveAvgPool -> 1x1x512

CLASSIFIER (3-layer MLP):
  FC(512->512) + ReLU + Dropout(0.3)
  FC(512->256) + ReLU + Dropout(0.2)
  FC(256->60)  -> 60 logits -> sigmoid > 0.5 -> binary

CRITICAL: Always float32 (BN overflows in FP16)
```

### 3.3 PatchGAN Discriminator
- Input: concatenated cover+stego (6ch) | 5 conv layers + spectral norm on ALL
- Output: patch-level real/fake scores | LeakyReLU(0.2)

### 3.4 Training Objective
```
L = 50*L_BCE + 0.01*L_VGG + 0.1*L_SSIM + 0.001*L_adv
```
Delta scale: annealed 0.30->0.38 over first 80 epochs, stays at 0.38 after.

### 3.5 Config
```
message_bits=60, batch=8, lr_g=1e-4, lr_r=3e-4, lr_d=3e-5
grad_clip_g=2.0, grad_clip_r=5.0, ema_decay=0.999
Mixed precision: FP16 encoder, FP32 decoder
```

---

## 4. ECC Scheme

GAN is **agnostic to ECC** - always encodes 60 random bits. ECC is external pre/post-processing. No retraining needed to change factor.

**Formula:** P_correct(p,n) = Sum C(n,k)*p^k*(1-p)^(n-k) for k=ceil(n/2) to n

| Rep | Data Bits | P_bit | P_token | Verdict |
|-----|-----------|-------|---------|---------|
| 3x  | 20        | 0.954 | 0.390   | Insufficient |
| 5x  | 12        | 0.985 | 0.834   | Marginal |
| 7x  | 8         | 0.993 | 0.945   | Acceptable |
| **10x** | **6** | **0.993** | **0.959** | **Chosen** |

---

## 5. Results (E464, 200-image test set)

| Metric | Value |
|--------|-------|
| Raw bit accuracy | 86.93% |
| ECC per-bit (10x) | ~99.3% |
| Token recovery | ~95.9% |
| PSNR | 26.24 dB |
| SSIM | 0.9514 |
| BER raw / ECC | 13.07% / ~0.7% |

### Multi-Capacity: 60-bit=86.93%, 120-bit=62.6%, 216-bit=58.5%

---

## 6. Dataset
- **Source:** Animals-10 + Animal Faces (Kaggle), 42,309 total
- **Training:** 10,000 randomly sampled | **Eval:** 200 held-out
- **Preprocessing:** center-crop -> 256x256 -> normalize [-1,1] -> random h-flip (train)

---

## 7. Bug & Failure History

**7.1 Visual Artifacts (Pink Cast + Green Banding)**
- Root cause: lambda_msg/lambda_percep = 5000:1. G learned structured patterns.
- Fix ready: Cell 8 fine-tuning with TV loss (not yet applied)

**7.2 PSNR Auto-Correction** - Never fired (PSNR was 22dB, threshold was 35dB)

**7.3 Training vs Eval PSNR** - Training 22-23dB (with noise layer) vs Eval 26.24dB (no noise). Expected.

**7.4 AMP Overflow** - ~30-epoch oscillation cycle. Normal, self-recovering.

**7.5 Fixed Bugs:** Broken checkpoint loaders, inverted delta annealing, feature collapse in 216-bit, false abort condition (psnr<25)

---

## 8. Security Analysis

Full recovery requires ALL FOUR: stego image + decoder weights + server + PIN/salt

| Attack | Gets | Outcome |
|--------|------|---------|
| Extract bits (L4-5) | 6 encrypted bits | Meaningless without PIN |
| Server (L2) | AES ciphertext | Can't decrypt (2^256) |
| Server + bits | Both | Can't link without XOR key |
| PIN + bits | Token 0-63 | No meaning without server |
| **All four** | Full message | Symmetric crypto ceiling |

**vs HiDDeN:** Steal decoder -> extract payload -> game over  
**vs Cyborg:** Steal decoder -> get number "42" -> completely useless

---

## 9. Backend Files

| File | Purpose |
|------|---------|
| `app.py` | FastAPI: /encode, /decode, /health, /images, /table/* |
| `model.py` | EncoderG + DecoderR + PatchGAN + NoiseLayer |
| `crypto.py` | AES-256-GCM (PyCryptodome) |
| `encryption.py` | Token->XOR+PBKDF2->10x ECC->60 bits |
| `decryption.py` | 60 bits->majority vote->XOR->token |
| `lookup_table.py` | JSON table, max 63 entries, FIFO eviction |
| `lsb.py` | Deterministic LSB scrambling |
| `ecc.py` | **STALE/UNUSED** - has old 3x config. Active code = encryption.py/decryption.py |

---

## 10. Viva Q&A

**Q: Why not embed the message directly?**
A: Decoder compromise exposes ciphertext for offline brute-force. Cyborg yields only a number 0-63.

**Q: Why is PSNR only 26 dB vs HiDDeN's 33 dB?**
A: We embed 60 bits at 256x256 vs 30 bits at 128x128. SSIM 0.9514 > 0.95 threshold confirms quality.

**Q: Why 10x repetition not BCH/LDPC?**
A: Only 6 bits need protection. 10x is simple, analyzable, gives 99.3%. BCH/LDPC overkill for 6 bits.

**Q: What does the SE block do?**
A: Learns which channels can carry message bits without perceptible distortion via channel-wise reweighting.

**Q: Why does decoder run in float32?**
A: BatchNorm overflows under FP16. Keeping decoder in float32 prevents NaN while encoder gets FP16 speedup.

**Q: Why did artifacts appear?**
A: Message loss dominated 5000:1 over perceptual losses. G found structured patterns more gradient-efficient.

**Q: How do you fix artifacts?**
A: TV loss penalizes spatial structure in delta map. Fine-tuning: increase perceptual weight 5x + add TV loss.

**Q: Training PSNR 22 dB vs eval 26 dB?**
A: Training includes noise layer (Gaussian + dropout). Eval disables noise -> cleaner stego -> higher PSNR.

**Q: What if server goes down?**
A: Messages unrecoverable. By design - server is single point of security. Destroying it destroys all messages.

**Q: What's the max message capacity?**
A: Token space: 64 entries. Each entry stores arbitrary-length AES ciphertext. Bottleneck is token count, not message size.

**Q: Why U-Net architecture?**
A: Skip connections preserve spatial detail. Multi-scale injection distributes bits across frequencies. Better than plain encoder which produces visible artifacts.

**Q: Is PBKDF2 with 100k iterations secure?**
A: Yes - meets OWASP recommendation. Domain separation ensures key independence.

**Q: What happens if someone trains their own decoder?**
A: Same result - they get a number 0-63. Without PIN, salt, and server, it's semantically empty.

---

## 11. Key Numbers

| Number | Meaning |
|--------|---------|
| 60 | Wire bits per image |
| 6 | Data bits after 10x ECC |
| 64 | Token space (2^6) |
| 0.38 | Final delta scale |
| 86.93% | Raw bit accuracy |
| 99.3% | ECC per-bit accuracy |
| 95.9% | Token recovery rate |
| 26.24 dB | PSNR |
| 0.9514 | SSIM |
| 5000:1 | lambda_msg/lambda_percep ratio |
| 100,000 | PBKDF2 iterations |
| 42,309 | Total dataset |
| 10,000 | Training subset |
| 464 | Best checkpoint epoch |
| 25 | IEEE paper citations |
