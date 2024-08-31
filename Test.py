import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import requests
import io
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
API_KEY = os.getenv("RAPIDAPI_KEY")

st.title("Image Rectangle Selection, Cropping, and Text Extraction")

# Function to crop the image based on a bounding box
def crop_image(image, bbox):
    return image.crop(bbox)

# Function to extract text from an image using the OCR API
def extract_text_from_image(image):
    url = "https://ocr-extract-text.p.rapidapi.com/ocr"
    
    # Save image to a BytesIO object to send as file
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    buffered.seek(0)
    
    files = {'image': buffered}
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "ocr-extract-text.p.rapidapi.com",
    }
    
    # Send the image file in a POST request
    response = requests.post(url, files=files, headers=headers)
    response_json = response.json()
    extracted_text = response_json.get("text", "No text found")  # Adjust based on actual JSON structure
    return extracted_text

# Function to clean up text by removing specified words
def clean_text(text, words_to_remove):
    for word in words_to_remove:
        text = text.replace(word, "")
    return text.strip()

# Upload the image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

if uploaded_file:
    try:
        # Open and convert the image to RGB format to avoid compatibility issues
        im2_reg = Image.open(uploaded_file).convert("RGB")
        
        # Display the uploaded image in the sidebar
        st.sidebar.image(im2_reg, caption="Uploaded Image", use_column_width=True)
        
        # Define the fixed size for the canvas
        canvas_width, canvas_height = 800, 600
        
        # Resize image to fit the canvas size
        im2_reg_resized = im2_reg.resize((canvas_width, canvas_height))
        
        # Display the image directly in the canvas for rectangle selection
        st.write("Draw two rectangles on the image to select regions of interest:")
        
        # Create a canvas with drawing mode set to rectangles
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)", 
            stroke_color="red",
            stroke_width=2,
            background_image=im2_reg_resized,
            height=canvas_height,
            width=canvas_width,
            drawing_mode="rect",  # Set drawing mode to rectangle
            key="canvas",
            display_toolbar=True,
        )

        if canvas_result.json_data is not None:
            # Get the drawn rectangles
            selected_objects = canvas_result.json_data["objects"]
            if len(selected_objects) == 2:
                # Extract bounding boxes for each of the two drawn rectangles
                bboxes = []
                for obj in selected_objects:
                    x, y = int(obj["left"]), int(obj["top"])
                    w, h = int(obj["width"]), int(obj["height"])
                    bboxes.append((x, y, x + w, y + h))

                # Convert bounding box coordinates back to original image scale
                scale_x = im2_reg.width / canvas_width
                scale_y = im2_reg.height / canvas_height
                bboxes = [
                    (
                        int(bbox[0] * scale_x), int(bbox[1] * scale_y),
                        int(bbox[2] * scale_x), int(bbox[3] * scale_y)
                    )
                    for bbox in bboxes
                ]
                
                # Crop the image based on the bounding boxes
                im2_cropped1 = crop_image(im2_reg, bboxes[0])
                im2_cropped2 = crop_image(im2_reg, bboxes[1])
                
                # Display the cropped images
                st.image(im2_cropped1, caption="Cropped Image 1", use_column_width=True)
                st.image(im2_cropped2, caption="Cropped Image 2", use_column_width=True)
                
                # Extract text from cropped images
                st.write("Extracting text from cropped images...")
                text1 = extract_text_from_image(im2_cropped1)
                text2 = extract_text_from_image(im2_cropped2)
                
                # Clean up text by removing unwanted words
                text2_cleaned = clean_text(text2, ["Expéditeur", "المرسل"])
                
                # Display the extracted text in a table
                data = {
                    "Code Bar": [text1],
                    "Expediteur": [text2_cleaned],
                }
                df = pd.DataFrame(data, index=["Extracted Text"])
                st.table(df)
               
            else:
                st.write("Please draw exactly two rectangles.")
    except Exception as e:
        st.error(f"An error occurred while processing the image: {e}")
else:
    st.write("Please upload an image to start.")
