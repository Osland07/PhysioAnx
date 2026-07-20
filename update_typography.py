import os

def replace_in_files(directory):
    color_map = {
        "#2D3748": "#002C6F",  # Main dark text to Deep Navy
        "#4A5568": "#1E3F76",  # Secondary dark text to Lighter Navy
    }
    
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') or file.endswith('.qss'):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                changed = False
                for old_c, new_c in color_map.items():
                    if old_c in content:
                        content = content.replace(old_c, new_c)
                        changed = True
                        
                if changed:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    count += 1
                    print(f"Updated: {file_path}")
                    
    print(f"Complete. Updated {count} files.")

if __name__ == "__main__":
    replace_in_files(r"C:\Users\oslan\Documents\Programming\PhysioAnx\app")
