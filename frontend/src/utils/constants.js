// Legacy charset — no longer enforced by the token architecture.
// The backend maps any message to a 6-digit reference number.
export const CHARSET = "Abcd...123 @#$%&*";

export const ENCODE_STEPS = [
  { label: "Select Image", description: "Choose a cover image" },
  { label: "Enter Details", description: "Message & credentials" },
  { label: "Result", description: "Download stego image" },
];

export const DECODE_STEPS = [
  { label: "Upload Image", description: "Upload stego image" },
  { label: "Enter Details", description: "Enter credentials" },
  { label: "Result", description: "Recovered message" },
];
