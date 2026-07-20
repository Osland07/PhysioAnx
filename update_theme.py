import os

files_to_update = [
    r"C:\Users\oslan\Documents\Programming\PhysioAnx\app\assets\styles\theme.qss",
    r"C:\Users\oslan\Documents\Programming\PhysioAnx\app\components\patient_dialog.py",
    r"C:\Users\oslan\Documents\Programming\PhysioAnx\app\login_window.py",
    r"C:\Users\oslan\Documents\Programming\PhysioAnx\app\main_window.py"
]

color_map = {
    "#0083B0": "#4F97D1",
    "#00B4DB": "#5C9EDA",
    "#00D2FF": "#75B0E1"
}

for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        for old_color, new_color in color_map.items():
            content = content.replace(old_color, new_color)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
print("Theme update complete.")
