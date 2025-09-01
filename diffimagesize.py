# Importing required packages
import cv2
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap

# === Configuration ===
image_folder = r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\images2"
output_video = "Modified_DiffImageSize_Video.mp4"
font_size = 16
line_spacing = font_size + 5
max_lines = 4
text_padding = 10
blue_bg = (90, 40, 10)
fps = 30

# Gaps
image_gap_x = 40
image_gap_y = 60
side_padding = 50
top_padding = 30

# Target size for image area (before adding text)
TARGET_IMG_WIDTH = 300
TARGET_IMG_HEIGHT = 400

# Timings
seconds_per_frame = 3
repeats_per_frame = fps * seconds_per_frame
slide_duration = 1  # seconds for entry animation
slide_frames = int(fps * slide_duration)

# === Descriptions ===
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

# === Object-fit: cover logic ===
def object_fit_cover(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height
    if img_ratio > target_ratio:
        # Wider than target: fit height, crop width
        scale = target_height / img.height
        new_width = int(scale * img.width)
        img = img.resize((new_width, target_height), Image.LANCZOS)
        left = (new_width - target_width) // 2
        img = img.crop((left, 0, left + target_width, target_height))
    else:
        # Taller than target: fit width, crop height
        scale = target_width / img.width
        new_height = int(scale * img.height)
        img = img.resize((target_width, new_height), Image.LANCZOS)
        top = (new_height - target_height) // 2
        img = img.crop((0, top, target_width, top + target_height))
    return img

# === Load and preprocess images ===
def load_images():
    images = []
    for i in range(1, len(descriptions) + 1):
        path = os.path.join(image_folder, f"{i}.jpg")
        if not os.path.exists(path):
            raise ValueError(f"Image {path} not found.")
        pil_img = Image.open(path).convert("RGB")
        fitted_img = object_fit_cover(pil_img, TARGET_IMG_WIDTH, TARGET_IMG_HEIGHT)
        images.append(cv2.cvtColor(np.array(fitted_img), cv2.COLOR_RGB2BGR))
    return images

# === Add wrapped description to image (below original) ===
def add_description(img, text):
    h, w = img.shape[:2]
    text_height = line_spacing * max_lines + text_padding
    new_img = np.full((h + text_height, w, 3), blue_bg, dtype=np.uint8)
    new_img[:h] = img

    pil_img = Image.fromarray(new_img)
    draw = ImageDraw.Draw(pil_img)
    font_path = r"C:/Windows/Fonts/arial.ttf"
    font = ImageFont.truetype(font_path, font_size)

    wrap_width = max(10, w // (font_size // 2))
    lines = textwrap.wrap(text, width=wrap_width)
    y_text = h + 5
    for line in lines[:max_lines]:
        w_text = draw.textlength(line, font=font)
        draw.text(((w - w_text) // 2, y_text), line, font=font, fill=(255, 255, 255))
        y_text += line_spacing

    return np.array(pil_img)

# === Compute maximum frame size based on 2x2 layout ===
def compute_frame_size(blocks):
    rows = [blocks[i:i + 2] for i in range(0, len(blocks), 2)]
    max_width = 0
    total_height = 0
    for row in rows:
        row_width = sum(b.shape[1] for b in row) + image_gap_x * (len(row) - 1)
        row_height = max(b.shape[0] for b in row)
        max_width = max(max_width, row_width)
        total_height += row_height
    max_width += side_padding * 2
    total_height += image_gap_y * (len(rows) - 1) + top_padding * 2
    return (max_width, total_height)

# === Combine blocks into a frame with optional x_offset ===
def make_frame(img_blocks, frame_size, x_offset=0):
    canvas = np.full((frame_size[1], frame_size[0], 3), blue_bg, dtype=np.uint8)
    y_cursor = top_padding
    row_blocks = [img_blocks[i:i + 2] for i in range(0, len(img_blocks), 2)]
    for row in row_blocks:
        row_height = max(block.shape[0] for block in row)
        x_cursor = side_padding
        for block in row:
            h, w = block.shape[:2]
            x_pos = x_cursor + x_offset
            y_pos = y_cursor + (row_height - h) // 2
            if 0 <= x_pos < frame_size[0] and x_pos + w <= frame_size[0]:
                canvas[y_pos:y_pos + h, x_pos:x_pos + w] = block
            x_cursor += w + image_gap_x
        y_cursor += row_height + image_gap_y
    return canvas

# === Slide-in animation ===
def slide_in_animation(blocks, frame_size):
    frames = []
    for f in range(slide_frames):
        progress = f / slide_frames
        x_offset = int((1 - progress) * frame_size[0])
        frame = make_frame(blocks, frame_size, x_offset)
        frames.append(frame)
    return frames

# === Main execution ===
def generate_video():
    images = load_images()
    annotated = [add_description(img, desc) for img, desc in zip(images, descriptions)]
    groups = [annotated[i:i + 4] for i in range(0, len(annotated), 4)]

    frame_sizes = [compute_frame_size(g) for g in groups]
    frame_width = max(f[0] for f in frame_sizes)
    frame_height = max(f[1] for f in frame_sizes)
    fixed_frame_size = (frame_width, frame_height)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, fixed_frame_size)

    for idx, group in enumerate(groups):
        print(f"Rendering group {idx + 1}/{len(groups)}...")

        if idx == 0:
            frame = make_frame(group, fixed_frame_size)
            for _ in range(repeats_per_frame):
                out.write(frame)
        else:
            anim_frames = slide_in_animation(group, fixed_frame_size)
            for f in anim_frames:
                out.write(f)
            final_frame = make_frame(group, fixed_frame_size)
            for _ in range(repeats_per_frame):
                out.write(final_frame)

    out.release()
    print("Video saved to:", output_video)

if __name__ == "__main__":
    generate_video()