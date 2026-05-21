from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import torch
import numpy as np
from PIL import Image
import requests
import io
import random
import torchvision.transforms as T

from model import EncoderG, DecoderR
from crypto import aes_encrypt, aes_decrypt
from encryption import encrypt
from decryption import decrypt
from lookup_table import add_message, get_message, list_entries, remove_entry
from lsb import add_lsb_noise, remove_lsb_noise

# ═══════════════════════════════════════════
#  FastAPI app
# ═══════════════════════════════════════════
app = FastAPI(title="Cyborg — StegoGAN v9.1 API")

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # restrict to your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Ref-Number"],  # let frontend read custom headers
)

# ═══════════════════════════════════════════
#  Load model once at startup
# ═══════════════════════════════════════════
device = "cpu"
G = EncoderG(msg_bits=60).to(device)
R = DecoderR(msg_bits=60).to(device)

ckpt = torch.load("ckpt_e464.pth", map_location=device, weights_only=False)
G.load_state_dict(ckpt["G"])       # use regular weights (matches Colab demo)
R.load_state_dict(ckpt["R"])
G.eval()
R.eval()

transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(256),
    T.ToTensor(),
    T.Normalize([0.5] * 3, [0.5] * 3),
])


# ═══════════════════════════════════════════
#  GET / and /health
# ═══════════════════════════════════════════
@app.get("/")
def root():
    """Root — HF Spaces health check hits this."""
    return {"name": "Cyborg StegoGAN v9.1", "status": "running", "bits": 60}

@app.get("/health")
def health():
    """Health check — also useful to wake up sleeping HF Space."""
    return {"status": "ok", "model": "StegoGAN v9.1", "bits": 60}


# ═══════════════════════════════════════════
#  Pydantic models for table endpoints
# ═══════════════════════════════════════════
class TableAddRequest(BaseModel):
    message: str

class TableLookupRequest(BaseModel):
    ref_number: str


# ═══════════════════════════════════════════
#  Dataset config
# ═══════════════════════════════════════════
HF_DATASET = "StrawHat7/coice_animal"
HF_DATASET_SPLIT = "train"
HF_DATASET_TOTAL = 150  # total images in the dataset


# ═══════════════════════════════════════════
#  GET /images
# ═══════════════════════════════════════════
@app.get("/images")
def get_images(random_count: int = 9):
    """
    Return `random_count` random image URLs from the HF dataset.
    Uses the HF datasets-server API to get signed CDN URLs.
    """
    random_count = min(random_count, 20)  # cap to prevent abuse

    # Pick random offsets from the dataset
    indices = random.sample(range(HF_DATASET_TOTAL), min(random_count, HF_DATASET_TOTAL))

    images = []
    for idx in indices:
        try:
            url = (
                f"https://datasets-server.huggingface.co/rows"
                f"?dataset={HF_DATASET}"
                f"&config=default"
                f"&split={HF_DATASET_SPLIT}"
                f"&offset={idx}&length=1"
            )
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            row = resp.json()["rows"][0]["row"]
            images.append(row["image"]["src"])
        except Exception:
            continue  # skip failed fetches silently

    return {"images": images}


# ═══════════════════════════════════════════
#  POST /table/add
# ═══════════════════════════════════════════
@app.post("/table/add")
def table_add(req: TableAddRequest):
    """Add a message to the lookup table, returns the assigned reference number."""
    ref = add_message(req.message)
    return {"ref_number": ref}


# ═══════════════════════════════════════════
#  POST /table/lookup
# ═══════════════════════════════════════════
@app.post("/table/lookup")
def table_lookup(req: TableLookupRequest):
    """Look up a reference number, returns the original message."""
    msg = get_message(req.ref_number)
    if msg is None:
        return {"error": f"Reference number {req.ref_number} not found"}
    return {"message": msg}


# ═══════════════════════════════════════════
#  POST /table/list
# ═══════════════════════════════════════════
@app.get("/table/list")
def table_list():
    """List all entries in the lookup table."""
    return {"entries": list_entries()}


# ═══════════════════════════════════════════
#  POST /encode
# ═══════════════════════════════════════════
@app.post("/encode")
def encode(
    image_url: str    = Form(None),
    image_file: UploadFile = File(None),
    message: str      = Form(...),
    pin: str          = Form(...),
    salt: str         = Form(...),
):
    # 1. Load cover image from URL or uploaded file
    if image_file and image_file.filename:
        img = Image.open(image_file.file).convert("RGB")
    elif image_url:
        img = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Provide image_url or image_file")
    tensor = transform(img).unsqueeze(0).to(device)

    # 2. AES-256-GCM encrypt message → store ciphertext in table → ref_number
    ciphertext = aes_encrypt(message, pin, salt)
    ref_number = add_message(ciphertext)

    # 3. ref_number → XOR+PBKDF2 → 10× ECC → 60 bits
    ecc_bits = encrypt(int(ref_number), pin, salt)

    msg_tensor = torch.tensor(
        ecc_bits, dtype=torch.float32
    ).unsqueeze(0).to(device)

    # 4. StegoGAN encode
    with torch.no_grad():
        stego = G(tensor, msg_tensor, 0.38)

    # 5. Tensor → numpy uint8
    stego_np = (
        (stego.squeeze().permute(1, 2, 0).cpu().numpy() + 1) / 2 * 255
    ).astype(np.uint8)

    # 6. Add LSB noise
    stego_np = add_lsb_noise(stego_np, pin, salt)

    # 7. Return as PNG stream
    img_out = Image.fromarray(stego_np)
    buf = io.BytesIO()
    img_out.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"X-Ref-Number": ref_number},  # pass token back to sender
    )


# ═══════════════════════════════════════════
#  POST /decode
# ═══════════════════════════════════════════
@app.post("/decode")
def decode(
    file: UploadFile = File(...),
    pin: str         = Form(...),
    salt: str        = Form(...),
):
    # 1. Read uploaded stego image
    stego_np = np.array(Image.open(file.file).convert("RGB"))

    # 2. Remove LSB noise
    stego_np = remove_lsb_noise(stego_np, pin, salt)

    # 3. Numpy → tensor (reuse same transform as encode side)
    tensor = transform(Image.fromarray(stego_np)).unsqueeze(0).to(device)

    # 4. StegoGAN decode
    with torch.no_grad():
        pred = (torch.sigmoid(R(tensor)) > 0.5).float().squeeze()

    # 5. Raw 60 bits from StegoGAN R
    bits_60 = pred.cpu().int().tolist()

    # 6. XOR+PBKDF2 decrypt → ref_number
    ref_number = decrypt(bits_60, pin, salt)

    # 7. Lookup → AES ciphertext
    ciphertext = get_message(ref_number)

    # 8. AES-256-GCM decrypt → original message
    if ciphertext:
        message = aes_decrypt(ciphertext, pin, salt)
        if message is None:
            message = "[Decryption failed — wrong PIN/salt or corrupted data]"
    else:
        message = f"[Token {ref_number} not found in table]"

    return {
        "ref_number": ref_number,
        "message": message,
    }
