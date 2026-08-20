import os, glob, re

path = r"c:\Users\sbhar\OneDrive\Documents\sentinal 2A\crop-classification-project\templates\*.html"
files = glob.glob(path)

arc_html = """
        <!-- ===== ARC MENU ===== -->
        <div class="arc-menu">
           <div class="arc-reactor">
              <div class="core"></div>
              <div class="ring one"></div>
              <div class="ring two"></div>
              <div class="ring three"></div>
           </div>
           <nav class="arc-nav">
              <a href="/" class="arc-item" data-tooltip="Dashboard">🏠</a>
              <a href="/upload" class="arc-item" data-tooltip="Upload Image">📤</a>
              <a href="/models" class="arc-item" data-tooltip="Model Comparison">📊</a>
              <a href="/#about" class="arc-item" data-tooltip="About Project">ℹ️</a>
           </nav>
        </div>
        
        <!-- ===== MAIN CONTENT ===== -->
"""

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove sidebar
    content = re.sub(r'<!-- ===== SIDEBAR ===== -->.*?<div class="sidebar-overlay"[^>]*></div>', '', content, flags=re.DOTALL)
    
    # Remove toggle button
    content = re.sub(r'<button class="nav-toggle"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
    content = re.sub(r'<button class="mobile-toggle"[^>]*>.*?</button>', '', content, flags=re.DOTALL)

    # Update template
    if '<!-- ===== ARC MENU ===== -->' not in content:
        content = content.replace('<!-- ===== MAIN CONTENT ===== -->', arc_html)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("HTML templates modified successfully for Arc Menu.")
