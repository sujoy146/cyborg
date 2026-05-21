import hashlib
import numpy as np


def _get_lsb_pattern(image_array, pin, salt):
    """Generate deterministic LSB noise pattern from PIN+salt.
    Uses domain-separated key ('cyborg-lsb:' prefix) for independence
    from AES and XOR layers.
    """
    key = f"{pin}cyborg-lsb:{salt}"
    seed = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed=seed)
    return rng.integers(0, 2, size=image_array.shape).astype(np.uint8)


def add_lsb_noise(image_array, pin, salt):
    """Add deterministic LSB noise to image (encode side)."""
    noise = _get_lsb_pattern(image_array, pin, salt)
    return (image_array & np.uint8(0xFE)) | noise


def remove_lsb_noise(image_array, pin, salt):
    """Remove deterministic LSB noise from image (decode side).
    Same operation as add — XOR-like: applying the same pattern undoes it.
    """
    noise = _get_lsb_pattern(image_array, pin, salt)
    return (image_array & np.uint8(0xFE)) | noise
