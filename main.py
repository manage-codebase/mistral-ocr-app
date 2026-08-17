import os
from mistralai.client import Mistral

# --- Setup ---
# Set your API key as an environment variable (safer than hardcoding):
#   export MISTRAL_API_KEY="your_key_here"
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# --- Point at your local file ---
input_path = "RBAC_PLAN.pdf"          # your PDF or image
output_path = "extracted_text.md"       # where to save the result

# --- Step 1: Upload the local file ---
with open(input_path, "rb") as f:
    uploaded = client.files.upload(
        file={"file_name": os.path.basename(input_path), "content": f},
        purpose="ocr",
    )

# --- Step 2: Get a temporary signed URL for the uploaded file ---
signed = client.files.get_signed_url(file_id=uploaded.id)

# --- Step 3: Run OCR ---
response = client.ocr.process(
    model="mistral-ocr-2512",           # OCR 3
    document={"type": "document_url", "document_url": signed.url},
)

# --- Step 4: Combine all pages and save ---
full_text = "\n\n".join(page.markdown for page in response.pages)

with open(output_path, "w", encoding="utf-8") as out:
    out.write(full_text)

print(f"Done. Extracted {len(response.pages)} page(s) to {output_path}")