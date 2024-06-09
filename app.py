import streamlit as st
import requests
import os
import io
from PIL import Image
from psd_tools import PSDImage

st.title('PSD Text Processor')

api_url = st.text_input("API URL", "http://localhost:8000")

uploaded_psd_file = st.file_uploader("Upload a PSD file", type=["psd"])
font_name = st.text_input("Enter font name", "NanumBarunGothicOTF")

if uploaded_psd_file is not None:
    # Save uploaded PSD file to a temporary location
    temp_dir = "temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    psd_temp_path = os.path.join(temp_dir, uploaded_psd_file.name)
    
    with open(psd_temp_path, "wb") as f:
        f.write(uploaded_psd_file.getbuffer())

    if st.button("Process PSD"):
        try:
            # Upload the PSD file
            with open(psd_temp_path, 'rb') as psd_file:
                files = {'file': psd_file}
                data = {'font_name': font_name}
                response = requests.post(f"{api_url}/upload/", files=files, data=data)
                response.raise_for_status()
                file_path = response.json().get("file_path")
            
            st.write("PSD file processed successfully.")
            
            # Download the processed PSD file
            download_response = requests.get(f"{api_url}/download/", params={'file_path': file_path})
            download_response.raise_for_status()
            processed_psd_content = download_response.content

            # Convert PSD to PNG for rendering
            processed_psd = io.BytesIO(processed_psd_content)
            psd = PSDImage.open(processed_psd)
            png_image = psd.compose().convert('RGB')
            png_image_io = io.BytesIO()
            png_image.save(png_image_io, format='PNG')
            png_image_io.seek(0)
            
            st.subheader("Processed PSD File")
            st.image(png_image_io, caption='Processed PSD as PNG')

            st.download_button("Download Processed PSD", processed_psd_content, "processed.psd")
            
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            st.text(str(e))  # Log the actual error for debugging
            
            # Additional debug information
            st.text(f"API URL: {api_url}")
            try:
                # Try a simple GET request to see if the server is reachable
                test_response = requests.get(api_url)
                st.text(f"Test connection response status code: {test_response.status_code}")
            except requests.exceptions.RequestException as test_e:
                st.text(f"Test connection failed: {test_e}")
