const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120000); // 120s (HF cold start)

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || body.message || `Server error ${res.status}`);
    }

    return res;
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Request timed out. The server may be busy — try again.");
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchGalleryImages() {
  const res = await request(`/images?random_count=9`);
  const data = await res.json();
  return data.images; // string[]
}

export async function encodeImage({ imageUrl, imageFile, message, pin, salt }) {
  // Backend /encode accepts either image_url (string) or image_file (upload)
  const formData = new FormData();
  if (imageFile) {
    formData.append("image_file", imageFile);
  } else {
    formData.append("image_url", imageUrl);
  }
  formData.append("message", message);
  formData.append("pin", pin);
  formData.append("salt", salt);

  const res = await request("/encode", {
    method: "POST",
    body: formData,
  });

  // Response is a PNG stream — convert to blob URL
  const blob = await res.blob();
  const stegoUrl = URL.createObjectURL(blob);
  const refNumber = res.headers.get("X-Ref-Number");

  return { stegoUrl, refNumber };
}

export async function decodeImage({ stegoImage, pin, salt }) {
  const formData = new FormData();
  formData.append("file", stegoImage);   // must match backend param name: file
  formData.append("pin", pin);
  formData.append("salt", salt);

  const res = await request("/decode", {
    method: "POST",
    body: formData,
  });
  const data = await res.json();
  // expects: { ref_number: string, message: string }
  return data;
}
