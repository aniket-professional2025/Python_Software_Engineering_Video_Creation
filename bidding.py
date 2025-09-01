# Importing required packages
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
WIDTH, HEIGHT = 1280, 720
FPS = 30
ITEM_DISPLAY_DURATION = 3
FRAMES_PER_ITEM = FPS * ITEM_DISPLAY_DURATION

# Set the output video file
output_video = "bidding_simulation_5.mp4"

# Load the resources
human_img = Image.open(r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\biddingimages\RemoveBg_Person_Hammer_Gavel.png").resize((400, 600)).convert("RGBA")
hammer_down_img = Image.open(r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\biddingimages\RemoveBg_Person_Hammer_Gavel_Touching.png").resize((400, 600)).convert("RGBA")
font_path = r"C:/Windows/Fonts/arial.ttf"
font_title = ImageFont.truetype(font_path, 30)
font_small = ImageFont.truetype(font_path, 24)

# Demo data
demo_data = [
    {
        "item_img": r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\biddingimages\Antique_Vase.jpg",
        "description": "Antique Vase - 18th Century porcelain from China.",
        "price": "₹12,000",
        "bidder": "Amit Sharma"
    },
    {
        "item_img": r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\biddingimages\Rolex_Image.jpg",
        "description": "Vintage Rolex Watch - Stainless steel with leather strap.",
        "price": "₹45,000",
        "bidder": "Riya Sen"
    },
    {
        "item_img": r"C:\Users\Webbies\Jupyter_Notebooks\VideoCreation_From_Image\biddingimages\Gogh_Painting.jpg",
        "description": "Oil Painting - Landscape by unknown 20th-century artist.",
        "price": "₹7,500",
        "bidder": "Karan Verma"
    },
]

# Helper: Draw text with wrapping
def draw_wrapped_text(draw, text, position, font, max_width, fill=(0, 0, 0)):
    lines = []
    words = text.split()
    while words:
        line_words = []
        while words:
            next_line = " ".join(line_words + [words[0]])
            text_width = font.getbbox(next_line)[2] - font.getbbox(next_line)[0]
            if text_width <= max_width:
                line_words.append(words.pop(0))
            else:
                break
        lines.append(" ".join(line_words))

    x, y = position
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        text_height = font.getbbox(line)[3] - font.getbbox(line)[1]
        y += text_height + 5

# Function to generate the frame
def create_frame(item_data, frame_count):
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # 1. Animated human with hammer (bidding animation)
    cycle_length = 20  # Total frames for one up+down motion
    in_strike_phase = (frame_count % cycle_length) < (cycle_length // 5)

    human_x = 20
    human_y = HEIGHT - human_img.height - 20

    if in_strike_phase:
        canvas.paste(hammer_down_img, (human_x, human_y), hammer_down_img)
    else:
        canvas.paste(human_img, (human_x, human_y), human_img)

    # 2. Item image (with alpha support)
    item_img = Image.open(item_data["item_img"]).resize((400, 400)).convert("RGBA")
    r, g, b, a = item_img.split()
    canvas.paste(item_img, (350, 100), a)

    # 3. Description
    draw.rectangle([(770, 100), (1220, 180)], outline="black", width=3)
    draw_wrapped_text(draw, item_data["description"], (780, 110), font=font_small, max_width=420)

    # 4. Current price
    draw.rectangle([(770, 320), (1220, 380)], fill="#E6FFE6", outline="green", width=2)
    draw.text((780, 335), f"Current Price: {item_data['price']}", font=font_title, fill=(0, 128, 0))

    # 5. Highest bidder
    draw.rectangle([(770, 400), (1220, 460)], fill="#FFF0F5", outline="purple", width=2)
    draw.text((780, 415), f"Highest Bidder: {item_data['bidder']}", font=font_title, fill=(128, 0, 128))

    # Convert to RGB before saving to video (OpenCV doesn't support alpha)
    return np.array(canvas.convert("RGB"))

# Create the Video writer object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(output_video, fourcc, FPS, (WIDTH, HEIGHT))

frame_index = 0
for i, item in enumerate(demo_data):
    for _ in range(FRAMES_PER_ITEM):
        frame = create_frame(item, frame_index)
        video.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        frame_index += 1

video.release()
print(f"Video saved as {output_video}")