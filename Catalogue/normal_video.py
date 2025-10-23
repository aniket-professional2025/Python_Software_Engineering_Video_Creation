# Importing required packages
import cv2
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# === Configuration ===
image_folder = r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\images"
output_video = "auction_showcase_11.avi"
image_size = (300, 400)  # Width x Height for each image
font_size = 18
fps = 30
codec = 'XVID'
seconds_per_frame = 3
repeats_per_frame = fps * seconds_per_frame
blue_bg = (90, 40, 10)

# Gap configuration between images
image_gap_x = 40  # Horizontal gap between images
image_gap_y = 60  # Vertical gap between rows

# Automatically calculate frame size
# 2 columns × image width + gap, 2 rows × image height + text + gap
frame_width = (image_size[0] * 2) + image_gap_x + 100  # Add padding
frame_height = (image_size[1] + 80) * 2 + image_gap_y + 100  # Add padding for text
frame_size = (frame_width, frame_height)

# === Input Descriptions ===
descriptions = [
    "Lorem Ipsum 1",
    "Lorem Ipsum 2",
    "Lorem Ipsum 1234",
    "Lorem Ipsum @123",
    "This is a long description that should automatically wrap into the next line if it exceeds the image width",
    "Another Saree Image description that might wrap",
    "Saree image 7",
    "Saree Image 8"
]

# === Load and Resize Images ===
def load_images():
    images = []
    for i in range(1, 9):
        path = os.path.join(image_folder, f"{i}.jpg")
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Image {path} not found or unreadable.")
        img = cv2.resize(img, image_size)
        images.append(img)
    return images

# === Add description below each image, with auto line wrap ===
def add_description(img, text):
    font_path = r"C:/Windows/Fonts/arial.ttf"
    font = ImageFont.truetype(font_path, font_size)

    max_width = image_size[0] - 20  # Allow some padding
    lines = []
    words = text.split()
    line = ""

    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)

    for word in words:
        test_line = line + " " + word if line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    h = img.shape[0]
    line_height = font_size + 8
    total_text_height = len(lines) * line_height + 20
    new_h = h + total_text_height

    new_img = np.full((new_h, image_size[0], 3), blue_bg, dtype=np.uint8)
    new_img[:h] = img

    pil_img = Image.fromarray(new_img)
    draw = ImageDraw.Draw(pil_img)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (image_size[0] - w) // 2
        y = h + 10 + i * line_height
        draw.text((x, y), line, fill=(255, 255, 255), font=font)

    return np.array(pil_img)

# === Combine 4 image-text blocks into a frame ===
def make_frame(img_blocks):
    canvas = np.full((frame_size[1], frame_size[0], 3), blue_bg, dtype=np.uint8)

    # Calculate positions with spacing
    x0, y0 = 50, 50  # Starting offset from top-left
    positions = [
        (x0, y0),
        (x0 + image_size[0] + image_gap_x, y0),
        (x0, y0 + image_size[1] + 80 + image_gap_y),
        (x0 + image_size[0] + image_gap_x, y0 + image_size[1] + 80 + image_gap_y)
    ]

    for (img, pos) in zip(img_blocks, positions):
        h, w = img.shape[:2]
        canvas[pos[1]:pos[1]+h, pos[0]:pos[0]+w] = img

    return canvas

# === Main Execution ===
def generate_video():
    images = load_images()
    annotated_imgs = [add_description(img, desc) for img, desc in zip(images, descriptions)]

    four_per_frame = [annotated_imgs[i:i+4] for i in range(0, len(annotated_imgs), 4)]

    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(output_video, fourcc, fps, frame_size)

    for group in four_per_frame:
        frame = make_frame(group)
        for _ in range(repeats_per_frame):
            out.write(frame)

    out.release()
    print("Video saved to:", output_video)

if __name__ == "__main__":
    generate_video()
