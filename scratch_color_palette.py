import sys
try:
    from PIL import Image
except ImportError:
    print("Pillow not installed.")
    sys.exit(1)

def get_color_palette(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")
    # Resize heavily to find general colors quickly
    img = img.resize((50, 50))
    pixels = list(img.getdata())
    
    # We want to find:
    # 1. The darkest color (likely the text/typography)
    # 2. The most dominant non-white/non-gray colors
    
    darkest = min(pixels, key=lambda p: p[0]+p[1]+p[2])
    
    color_freq = {}
    for p in pixels:
        # Quantize slightly to group similar colors
        q = (p[0]//10*10, p[1]//10*10, p[2]//10*10)
        color_freq[q] = color_freq.get(q, 0) + 1
        
    sorted_colors = sorted(color_freq.items(), key=lambda x: x[1], reverse=True)
    
    print(f"Darkest Color (Likely Text): #{darkest[0]:02x}{darkest[1]:02x}{darkest[2]:02x}")
    
    print("\nDominant Color Clusters:")
    found_colors = []
    for color, count in sorted_colors:
        r, g, b = color
        # Skip pure white/light gray background
        if r > 240 and g > 240 and b > 240:
            continue
            
        # Ensure we pick distinctly different colors
        is_distinct = True
        for fc in found_colors:
            dist = sum(abs(a - b) for a, b in zip(color, fc))
            if dist < 60: # If too similar, skip
                is_distinct = False
                break
                
        if is_distinct:
            found_colors.append(color)
            hex_c = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            print(f"- {hex_c} (RGB: {r}, {g}, {b}) - Count: {count}")
            
        if len(found_colors) >= 5:
            break

if __name__ == "__main__":
    get_color_palette(r"C:\Users\oslan\Documents\Programming\PhysioAnx\app\assets\images\Logo_Text.jpeg")
