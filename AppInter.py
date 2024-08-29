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

# access the API key from environment variables
API_KEY = os.getenv("RAPIDAPI_KEY")

st.title("Image Point Selection, Cropping, and Text Extraction")

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
    
    files = {
        'image': buffered
    }
    
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
        
        # Define the fixed size for the canvas
        canvas_width, canvas_height = 500, 300
        
        # Resize image to fit the canvas size
        im2_reg_resized = im2_reg.resize((canvas_width, canvas_height))
        
        # Check if the resized image is loading correctly
        st.write("Debug: Image loaded and resized successfully.")
        
        # Display the image directly in the canvas for point selection
        st.write("Click to select three regions of interest on the image:")
        
        # Create a canvas with a fixed size
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)", 
            stroke_color="red",
            stroke_width=5,
            background_image=im2_reg_resized,
            height=canvas_height,
            width=canvas_width,
            drawing_mode="point",
            key="canvas",
            display_toolbar=False,
        )

        if canvas_result.json_data is not None:
            # Get the selected points coordinates
            selected_objects = canvas_result.json_data["objects"]
            if len(selected_objects) == 12:
                # Extract coordinates of the twelve points (4 per region)
                points = [(obj["left"], obj["top"]) for obj in selected_objects]
                
                # Separate the points into three sets for three regions
                points_region1 = points[:4]
                points_region2 = points[4:8]
                points_region3 = points[8:]
                
                # Calculate bounding boxes for all three regions
                def get_bbox(points):
                    x_coords, y_coords = zip(*points)
                    xmin, ymin = max(min(x_coords), 0), max(min(y_coords), 0)
                    xmax, ymax = min(max(x_coords), canvas_width), min(max(y_coords), canvas_height)
                    return (xmin, ymin, xmax, ymax)

                bbox1 = get_bbox(points_region1)
                bbox2 = get_bbox(points_region2)
                bbox3 = get_bbox(points_region3)
                
                # Convert bounding box coordinates back to original image scale
                scale_x = im2_reg.width / canvas_width
                scale_y = im2_reg.height / canvas_height
                bbox1 = (
                    int(bbox1[0] * scale_x), int(bbox1[1] * scale_y),
                    int(bbox1[2] * scale_x), int(bbox1[3] * scale_y)
                )
                bbox2 = (
                    int(bbox2[0] * scale_x), int(bbox2[1] * scale_y),
                    int(bbox2[2] * scale_x), int(bbox2[3] * scale_y)
                )
                bbox3 = (
                    int(bbox3[0] * scale_x), int(bbox3[1] * scale_y),
                    int(bbox3[2] * scale_x), int(bbox3[3] * scale_y)
                )
                
                # Crop the image based on the bounding boxes
                im2_cropped1 = crop_image(im2_reg, bbox1)
                im2_cropped2 = crop_image(im2_reg, bbox2)
                im2_cropped3 = crop_image(im2_reg, bbox3)
                
                # Display the cropped images
                st.image(im2_cropped1, caption="Cropped Image 1", use_column_width=True)
                st.image(im2_cropped2, caption="Cropped Image 2", use_column_width=True)
                st.image(im2_cropped3, caption="Cropped Image 3", use_column_width=True)
                
                # Extract text from all cropped images
                st.write("Extracting text from cropped images...")
                text1 = extract_text_from_image(im2_cropped1)
                text2 = extract_text_from_image(im2_cropped2)
                text3 = extract_text_from_image(im2_cropped3)
                
                # Clean up text by removing unwanted words
                text2_cleaned = clean_text(text2, ["Expéditeur", "المرسل"])
                text3_cleaned = clean_text(text3, ["Destinataire", "المرسل إليه"])
                
                # Display the extracted text in a table
                data = {
                    "Code Bar": [text1],
                    "Expediteur": [text2_cleaned],
                    "Destinataire": [text3_cleaned]
                }
                df = pd.DataFrame(data, index=["Extracted Text"])
                st.table(df)
               
            else:
                st.write("Please select exactly twelve points (four for each region).")
    except Exception as e:
        st.error(f"An error occurred while processing the image: {e}")
else:
    st.write("Please upload an image to start.")
