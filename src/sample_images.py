"""
Helper to create synthetic demonstration images for Multimodal Vision testing
(e.g., used air filter, window seal gap, and clean room setup).
"""

from PIL import Image, ImageDraw, ImageFont
import os

def generate_sample_images(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Used Air Filter Sample Image
    img1 = Image.new("RGB", (600, 450), color=(140, 140, 140))
    d1 = ImageDraw.Draw(img1)
    # Draw filter pleats
    for x in range(40, 560, 25):
        d1.line([(x, 40), (x, 410)], fill=(70, 70, 70), width=12)
        d1.line([(x + 8, 40), (x + 8, 410)], fill=(110, 110, 110), width=4)
    # Dark soot patch in center
    d1.ellipse([(180, 120), (420, 330)], fill=(55, 55, 55, 200))
    d1.rectangle([(30, 30), (570, 420)], outline=(30, 30, 30), width=10)
    d1.text((50, 45), "HEPA FILTER INSPECTION - 5 MONTHS WINTER SMOG EXPOSURE", fill=(240, 240, 240))
    img1.save(os.path.join(output_dir, "sample_hepa_filter.jpg"), "JPEG")

    # 2. Window Frame Gap / Draft Sample
    img2 = Image.new("RGB", (600, 450), color=(210, 200, 185))
    d2 = ImageDraw.Draw(img2)
    # Window glass
    d2.rectangle([(80, 80), (520, 370)], fill=(160, 185, 200), outline=(80, 60, 40), width=15)
    # Visible gap/draft crack with outdoor smog
    d2.line([(520, 80), (520, 370)], fill=(40, 30, 20), width=8)
    d2.text((90, 95), "UNSEALED SASH - VISIBLE DRAFT GAP & SMOG LEAKAGE", fill=(20, 20, 20))
    d2.text((90, 130), "Outdoor PM2.5 Infiltration Point", fill=(180, 30, 30))
    img2.save(os.path.join(output_dir, "sample_window_gap.jpg"), "JPEG")

    # 3. DIY Corsi-Rosenthal Box Build
    img3 = Image.new("RGB", (600, 450), color=(230, 220, 205))
    d3 = ImageDraw.Draw(img3)
    # Box fan top
    d3.ellipse([(150, 80), (450, 380)], outline=(40, 90, 140), width=14)
    # Fan blades
    d3.line([(300, 80), (300, 380)], fill=(70, 120, 170), width=8)
    d3.line([(150, 230), (450, 230)], fill=(70, 120, 170), width=8)
    # Cardboard shroud ring
    d3.ellipse([(200, 130), (400, 330)], outline=(180, 120, 60), width=16)
    d3.rectangle([(100, 50), (500, 400)], outline=(140, 90, 40), width=10)
    d3.text((115, 60), "DIY CORSI-ROSENTHAL BOX (4x MERV-13 + FAN SHROUD)", fill=(20, 50, 80))
    img3.save(os.path.join(output_dir, "sample_diy_box_fan.jpg"), "JPEG")

if __name__ == "__main__":
    generate_sample_images("sample_images")
