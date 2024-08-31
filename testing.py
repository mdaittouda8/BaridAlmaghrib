import streamlit as st
from PIL import Image
import numpy as np
import cv2
from streamlit_drawable_canvas import st_canvas

# Set page layout
st.set_page_config(layout="wide")

# Title of the app
st.title("Image Cropper Using Rectangle Drawing")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Read the uploaded image and convert it to RGB
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    # Display the uploaded image in the sidebar for reference
    st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)

    st.write("Draw a rectangle on the canvas to select the region for cropping.")

    # Convert the NumPy array back to a PIL Image for canvas background
    pil_img_for_canvas = Image.fromarray(img_array)

    # Create a drawable canvas with the uploaded image as background
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",  # No fill color
        stroke_width=3,
        background_image=pil_img_for_canvas,  # Use PIL Image as background
        update_streamlit=True,
        width=pil_img_for_canvas.width,
        height=pil_img_for_canvas.height,
        drawing_mode="rect",  # Change drawing mode to rectangle
        key="canvas",
    )

    # Process the drawn rectangle when available
    if canvas_result.json_data is not None:
        # Get list of drawn objects
        objects = canvas_result.json_data["objects"]
        if objects:
            # Get the first drawn rectangle
            rect = objects[0]
            x, y = int(rect["left"]), int(rect["top"])
            w, h = int(rect["width"]), int(rect["height"])

            # Crop the image using the rectangle coordinates
            cropped_img = img_array[y:y + h, x:x + w]

            # Display the cropped image
            st.image(cropped_img, caption="Cropped Image", use_column_width=True)
        else:
            st.warning("Please draw a rectangle to crop.")
else:
    st.info("Please upload an image to begin.")
