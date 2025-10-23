# Importing required packages
import cv2
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap

# === Configuration ===
image_folder = r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\images"
output_video = "Animated_Video_BgImage.mp4"
image_size = (300, 400)  # Width x Height
font_size = 14
line_spacing = font_size + 5
max_lines = 4
text_height = line_spacing * max_lines + 5
bg_image_path = r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\images2\8.jpg"

block_size = (image_size[0], image_size[1] + text_height)
image_gap_x = 40
image_gap_y = 60
blue_bg = (90, 40, 10)
fps = 30

frame_width = image_size[0] * 2 + image_gap_x + 100
frame_height = (image_size[1] + text_height) * 2 + image_gap_y + 100
frame_size = (frame_width, frame_height)

seconds_per_frame = 3
repeats_per_frame = fps * seconds_per_frame
slide_duration = 1  # seconds
slide_frames = int(fps * slide_duration)

descriptions = [
    "Lorem Ipsum 1",
    "Lorem Ipsum 2",
    "Lorem Ipsum 1234",
    "Lorem Ipsum @123",
    "Image Lorem Ipsum that is a very long description and should wrap to next line",
    "Saree Image Lorem Ipsum is also quite long and must be handled properly",
    "Saree image 7 is normal",
    "Saree Image 8 has moderate length"
]

# === Load and Resize Images ===
def load_images():
    images = []
    for i in range(1, len(descriptions) + 1):
        path = os.path.join(image_folder, f"{i}.jpg")
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Image {path} not found or unreadable.")
        img = cv2.resize(img, image_size)
        images.append(img)
    return images

# === Add description with word wrap ===
def add_description(img, text):
    h = img.shape[0]
    new_h = h + text_height
    new_img = np.full((new_h, image_size[0], 3), blue_bg, dtype=np.uint8)
    new_img[:h] = img

    pil_img = Image.fromarray(new_img)
    draw = ImageDraw.Draw(pil_img)
    font_path = r"C:/Windows/Fonts/arial.ttf"
    font = ImageFont.truetype(font_path, font_size)

    lines = textwrap.wrap(text, width=22)
    y_text = h + 5
    for line in lines[:max_lines]:
        w = draw.textlength(line, font=font)
        draw.text(((image_size[0] - w) // 2, y_text), line, font=font, fill=(255, 255, 255))
        y_text += line_spacing

    return np.array(pil_img)

# === Load and prepare background image ===
def get_background():
    bg = cv2.imread(bg_image_path)
    if bg is None:
        raise ValueError(f"Background image '{bg_image_path}' not found.")
    return cv2.resize(bg, frame_size)

# === Combine up to 4 image-text blocks with optional x_offset ===
def make_frame(img_blocks, x_offset=0):
    canvas = get_background()

    base_x = 50
    base_y = 30

    positions = [
        (base_x, base_y),
        (base_x + block_size[0] + image_gap_x, base_y),
        (base_x, base_y + block_size[1] + image_gap_y),
        (base_x + block_size[0] + image_gap_x, base_y + block_size[1] + image_gap_y)
    ]

    blank = np.full((block_size[1], block_size[0], 3), blue_bg, dtype=np.uint8)

    for i in range(4):
        img = img_blocks[i] if i < len(img_blocks) else blank
        x, y = positions[i]
        x += x_offset
        if 0 <= x < frame_size[0]:
            h, w = img.shape[:2]
            if x + w <= frame_size[0]:
                canvas[y:y + h, x:x + w] = img

    return canvas

# === Generate entry slide animation for a group ===
def slide_in_animation(img_blocks):
    frames = []
    for f in range(slide_frames):
        progress = f / slide_frames
        x_offset = int((1 - progress) * frame_size[0])
        frame = make_frame(img_blocks, x_offset)
        frames.append(frame)
    return frames

# === Main Execution ===
def generate_video():
    images = load_images()
    annotated_imgs = [add_description(img, desc) for img, desc in zip(images, descriptions)]
    groups = [annotated_imgs[i:i + 4] for i in range(0, len(annotated_imgs), 4)]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, frame_size)

    for idx, group in enumerate(groups):
        print(f"Rendering group {idx + 1}/{len(groups)}...")

        if idx == 0:
            final_frame = make_frame(group)
            for _ in range(repeats_per_frame):
                out.write(final_frame)
        else:
            slide_frames_group = slide_in_animation(group)
            for frame in slide_frames_group:
                out.write(frame)

            final_frame = make_frame(group)
            for _ in range(repeats_per_frame):
                out.write(final_frame)
    
    out.release()
    print("Video saved to:", output_video)

if __name__ == "__main__":
    generate_video()
