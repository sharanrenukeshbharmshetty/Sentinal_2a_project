import os, glob, re

path = r"c:\Users\sbhar\OneDrive\Documents\sentinal 2A\crop-classification-project\templates\*.html"
files = glob.glob(path)

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if "index.html" in f:
        title = "Dashboard"
    elif "upload.html" in f:
        title = "Upload Image"
    elif "models.html" in f:
        title = "Model Comparison"
    elif "result.html" in f:
        title = "Classification Results"
    else:
        title = "Overview"
        
    replacement = f'<div class="header-title" style="font-family: var(--font-display); font-size: 1.15rem; letter-spacing: 0.5px; color: rgba(255,255,255,0.9); font-weight: 500; text-transform: uppercase;">DeepCrop <span style="color: var(--accent); font-weight: 700;">AI</span> <span style="opacity: 0.3; margin: 0 12px;">|</span> <span style="font-weight: 400; font-size: 0.95rem; color: var(--text-muted);">{title}</span></div>'
    
    # Replace the existing header title
    content = re.sub(
        r'<div class="header-title">.*?</div>',
        replacement,
        content
    )
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("HTML updated with premium header titles.")
