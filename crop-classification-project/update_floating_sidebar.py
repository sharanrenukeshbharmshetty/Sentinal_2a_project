import os, glob, re

path = r"c:\Users\sbhar\OneDrive\Documents\sentinal 2A\crop-classification-project\templates\*.html"
files = glob.glob(path)

sidebar_html = """
        <!-- ===== FLOATING SIDEBAR BOX ===== -->
        <aside class="sidebar-box" id="sidebar">
            <div class="sidebar-header">
                <a href="/" class="sidebar-logo">
                    <span class="logo-icon">🛰️</span>
                    <span class="nav-text">Deep<span class="logo-accent">Crop</span> AI</span>
                </a>
            </div>
            <nav class="sidebar-nav">
                <a href="/" class="nav-item"><span class="nav-icon">🏠</span> <span class="nav-text">Dashboard</span></a>
                <a href="/upload" class="nav-item"><span class="nav-icon">📤</span> <span class="nav-text">Upload Image</span></a>
                <a href="/models" class="nav-item"><span class="nav-icon">📊</span> <span class="nav-text">Model Comparison</span></a>
                <a href="/#about" class="nav-item"><span class="nav-icon">ℹ️</span> <span class="nav-text">About Project</span></a>
            </nav>
            <div class="sidebar-footer">
                <p>© 2024 DeepCrop AI</p>
                <p>Final Year Project</p>
            </div>
        </aside>
        <div class="sidebar-overlay" id="sidebarOverlay"></div>

        <main class="main-content">
            <!-- Top Header -->
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
    
    # Remove ARC MENU to Top Header
    pattern = r'<!-- ===== ARC MENU ===== -->.*?<header class="top-header">'
    # Remove empty lines that were replaced
    pattern_empty_btn = r'\s*<div class="header-title">'
    
    content = re.sub(pattern, sidebar_html.rstrip(), content, flags=re.DOTALL)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("HTML templates modified successfully for Floating Sidebar.")
