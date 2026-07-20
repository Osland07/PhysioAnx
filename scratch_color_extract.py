import sys
from collections import Counter
try:
    from PIL import Image
except ImportError:
    print("Pillow not installed. Please install it.")
    sys.exit(1)

def get_dominant_colors(image_path, num_colors=10):
    img = Image.open(image_path)
    img = img.convert("RGB")
    img = img.resize((150, 150))
    pixels = list(img.getdata())
    
    # Filter out pure white/gray/black to find actual brand colors
    valid_pixels = []
    for p in pixels:
        r, g, b = p
        # if not completely white/gray
        if not (r > 240 and g > 240 and b > 240) and not (r < 20 and g < 20 and b < 20):
            # check if not perfectly gray (where r~=g~=b)
            if max(r,g,b) - min(r,g,b) > 20:
                valid_pixels.append(p)
                
    if not valid_pixels:
        valid_pixels = pixels

    counter = Counter(valid_pixels)
    most_common = counter.most_common(num_colors)
    
    for color, count in most_common:
        hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
        print(f"Color: {hex_color} (Count: {count}) RGB: {color}")

if __name__ == "__main__":
    get_dominant_colors(r"C:\Users\oslan\Documents\Programming\PhysioAnx\app\assets\images\Logo_Text.jpeg")
