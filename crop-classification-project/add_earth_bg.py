import os, glob, re

path = r"c:\Users\sbhar\OneDrive\Documents\sentinal 2A\crop-classification-project\templates\*.html"
files = glob.glob(path)

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        c = file.read()
    
    # 1. Remove old slideshow entirely
    c = re.sub(r'<div class="hero-slideshow">.*?</div>\s*<div class="hero-slideshow-overlay"></div>', '', c, flags=re.DOTALL)
    
    # 2. Add Earth Container to app-layout (right after sidebar-box/overlay)
    if '<div id="earth-container"' not in c:
        c = c.replace('<main class="main-content">', '<div id="earth-container"></div>\n        <main class="main-content">')
        
    # 3. Add Three.js to head or before script.js
    if 'three.min.js' not in c:
        if '<script src="{{ url_for(\'static\', filename=\'js/script.js\') }}"></script>' in c:
            c = c.replace('<script src="{{ url_for(\'static\', filename=\'js/script.js\') }}"></script>', 
                          '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n    <script src="{{ url_for(\'static\', filename=\'js/script.js\') }}"></script>')
        else:
            c = c.replace('</body>', '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n</body>')
            
    with open(f, 'w', encoding='utf-8') as file:
        file.write(c)

print("Added Earth Container & Three.js to HTML templates")
