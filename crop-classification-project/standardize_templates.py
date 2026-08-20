import os, glob, re

path = r"c:\Users\sbhar\OneDrive\Documents\sentinal 2A\crop-classification-project\templates\*.html"
files = glob.glob(path)

sidebar_box_html = """
        <!-- ===== FLOATING SIDEBAR BOX ===== -->
        <aside class="sidebar-box" id="sidebar">
            <div class="sidebar-header">
                <a href="/" class="sidebar-logo">
                    <span class="logo-icon">🛰️</span>
                    <span class="nav-text">Deep<span class="logo-accent">Crop</span> AI</span>
                </a>
            </div>
            <nav class="sidebar-nav">
                <a href="/" class="nav-item {{ 'active' if request.path == '/' }}"><span class="nav-icon">🏠</span> <span class="nav-text">Dashboard</span></a>
                <a href="/upload" class="nav-item {{ 'active' if request.path == '/upload' }}"><span class="nav-icon">📤</span> <span class="nav-text">Upload Image</span></a>
                <a href="/models" class="nav-item {{ 'active' if request.path == '/models' }}"><span class="nav-icon">📊</span> <span class="nav-text">Model Comparison</span></a>
                <a href="/#about" class="nav-item"><span class="nav-icon">ℹ️</span> <span class="nav-text">About Project</span></a>
            </nav>
            <div class="sidebar-footer">
                <p>© 2024 DeepCrop AI</p>
                <p>Final Year Project</p>
            </div>
        </aside>
        <div class="sidebar-overlay" id="sidebarOverlay"></div>
"""

header_start = """
            <header class="top-header">
                <button class="nav-toggle" id="desktopToggle">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
"""

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Standardize Sidebar
    # Remove old sidebar if present
    content = re.sub(r'<aside class="sidebar".*?</aside>', '', content, flags=re.DOTALL)
    # Remove old sidebar-box if present (to avoid duplicates)
    content = re.sub(r'<!-- ===== FLOATING SIDEBAR BOX ===== -->.*?<div class="sidebar-overlay" id="sidebarOverlay"></div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<div class="sidebar-overlay" id="sidebarOverlay"></div>', '', content, flags=re.DOTALL)
    
    # Inject new sidebar-box right after app-layout
    content = content.replace('<div class="app-layout">', '<div class="app-layout">\n' + sidebar_box_html)
    
    # Standardize Header Toggle
    if '<button class="nav-toggle" id="desktopToggle">' not in content:
        content = content.replace('<header class="top-header">', header_start)
        
    # Standardize Earth Environment
    if '<div id="earth-container"></div>' not in content:
        content = content.replace('<main class="main-content">', '<div id="earth-container"></div>\n        <main class="main-content">')

    # Remove duplicates of earth-container if they exist
    content = content.replace('<div id="earth-container"></div>\n        <div id="earth-container"></div>', '<div id="earth-container"></div>')

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("All templates standardized with Floating Sidebar and 3D Earth.")
