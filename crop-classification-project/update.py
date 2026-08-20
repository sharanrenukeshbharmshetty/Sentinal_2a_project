import os, glob, re

path = r"c:\Users\sbhar\OneDrive\Documents\sentinal 2A\crop-classification-project\templates\*.html"
files = glob.glob(path)
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        c = file.read()
    c = c.replace('<button class="mobile-toggle" id="mobileToggle">☰</button>', '<button class="nav-toggle" id="desktopToggle">\n                    <span></span>\n                    <span></span>\n                    <span></span>\n                </button>')
    c = c.replace('<span>Deep<span class="logo-accent">Crop</span> AI</span>', '<span class="nav-text">Deep<span class="logo-accent">Crop</span> AI</span>')
    for icon, text in [('🏠', 'Dashboard'), ('📤', 'Upload Image'), ('📊', 'Model Comparison'), ('ℹ️', 'About Project')]:
        c = re.sub(rf'(<span class="nav-icon">{icon}</span>)\s*{text}', rf'\1 <span class="nav-text">{text}</span>', c)
    with open(f, 'w', encoding='utf-8') as file:
        file.write(c)

print("HTML files updated")
