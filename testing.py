import streamlit as st
from PIL import Image
import numpy as np
import cv2
from streamlit_drawable_canvas import st_canvas

# Set page layout
st.set_page_config(layout="wide")

# Title of the app
st.title("Image Cropper Using Selected Points")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Read the uploaded image and convert it to RGB
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    # Display the uploaded image in the sidebar for reference
    st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)

    st.write("Draw points on the canvas to select the region for cropping.")

    # Convert the NumPy array back to a PIL Image for canvas background
    pil_img_for_canvas = Image.fromarray(img_array)

    # Create a drawable canvas with the uploaded image as background
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",  # No fill color
        stroke_width=3,
        background_image=pil_img_for_canvas,  # Use PIL Image as background
        update_streamlit=True,
        width=pil_img_for_canvas.width/3,
        height=pil_img_for_canvas.height/3,
        drawing_mode="point",
        point_display_radius=5,  # Increase point size for better visibility
        key="canvas",
        #background_color="rgba(0, 0, 0, 0)"  # Ensure a default white background color
    )

    # Process points when available
    if canvas_result.json_data is not None:
        # Get list of points drawn
        points = canvas_result.json_data["objects"]
        if len(points) >= 4:
            st.write(f"Selected points: {[(point['left'], point['top']) for point in points]}")

            # Extract coordinates of the first 4 points
            coordinates = [(int(point['left']), int(point['top'])) for point in points[:4]]

            # Convert coordinates to numpy array and create bounding box
            pts = np.array(coordinates, np.int32)
            pts = pts.reshape((-1, 1, 2))

            # Calculate the bounding box from the points
            rect = cv2.boundingRect(pts)
            x, y, w, h = rect

            # Crop the image
            cropped_img = img_array[y:y + h, x:x + w]

            # Display the cropped image
            st.image(cropped_img, caption="Cropped Image", use_column_width=True)
        else:
            st.warning("Please select at least 4 points.")
else:
    st.info("Please upload an image to begin.")
