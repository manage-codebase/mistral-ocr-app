import os

import streamlit as st
from mistralai.client import Mistral

st.set_page_config(page_title="OCR Extractor", page_icon="📄")
st.title("📄 Document / Image OCR")
st.write("Upload a PDF or image and get the extracted text as Markdown.")

api_key = st.secrets.get("MISTRAL_API_KEY", os.environ.get("MISTRAL_API_KEY"))
if not api_key:
    st.error("MISTRAL_API_KEY is not set. Add it in Streamlit secrets.")
    st.stop()

client = Mistral(api_key=api_key)

uploaded_file = st.file_uploader("Choose a PDF or image", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None and st.button("Run OCR"):
    with st.spinner("Uploading and processing..."):
        uploaded = client.files.upload(
            file={"file_name": uploaded_file.name, "content": uploaded_file.getvalue()},
            purpose="ocr",
        )
        signed = client.files.get_signed_url(file_id=uploaded.id)

        is_image = uploaded_file.type.startswith("image/")
        document = (
            {"type": "image_url", "image_url": signed.url}
            if is_image
            else {"type": "document_url", "document_url": signed.url}
        )

        response = client.ocr.process(model="mistral-ocr-2512", document=document)
        full_text = "\n\n".join(page.markdown for page in response.pages)

    st.success(f"Extracted {len(response.pages)} page(s).")
    st.markdown(full_text)
    st.download_button(
        "Download as Markdown",
        data=full_text,
        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_extracted.md",
        mime="text/markdown",
    )
