/**
 * DeepCrop AI — Main JavaScript
 * Handles sidebar, upload, animations, particles
 */
document.addEventListener('DOMContentLoaded', function () {

    // ===== FLOATING SIDEBAR BOX TOGGLE =====
    var desktopToggle = document.getElementById('desktopToggle');
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');

    if (desktopToggle && sidebar) {
        desktopToggle.addEventListener('click', function () {
            sidebar.classList.toggle('expanded');
            desktopToggle.classList.toggle('active');
            if (overlay) {
                overlay.classList.toggle('active');
            }
        });
        if (overlay) {
            overlay.addEventListener('click', function () {
                sidebar.classList.remove('expanded');
                desktopToggle.classList.remove('active');
                overlay.classList.remove('active');
            });
        }
    }
    var dropZone = document.getElementById('dropZone');
    var fileInput = document.getElementById('fileInput');
    var dropContent = document.getElementById('dropContent');
    var previewContainer = document.getElementById('previewContainer');
    var imagePreview = document.getElementById('imagePreview');
    var previewInfo = document.getElementById('previewInfo');
    var removeImage = document.getElementById('removeImage');
    var classifyBtn = document.getElementById('classifyBtn');

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', function (e) {
            if (e.target.id !== 'removeImage' && !e.target.closest('#removeImage')) fileInput.click();
        });
        ['dragenter', 'dragover'].forEach(function (ev) {
            dropZone.addEventListener(ev, function (e) { e.preventDefault(); e.stopPropagation(); dropZone.classList.add('drag-over'); });
        });
        ['dragleave', 'drop'].forEach(function (ev) {
            dropZone.addEventListener(ev, function (e) { e.preventDefault(); e.stopPropagation(); dropZone.classList.remove('drag-over'); });
        });
        dropZone.addEventListener('drop', function (e) {
            if (e.dataTransfer.files.length > 0) { fileInput.files = e.dataTransfer.files; handleFile(e.dataTransfer.files[0]); }
        });
        fileInput.addEventListener('change', function (e) {
            if (e.target.files.length > 0) handleFile(e.target.files[0]);
        });
        if (removeImage) removeImage.addEventListener('click', function (e) { e.stopPropagation(); resetUpload(); });
    }

    function handleFile(file) {
        var ext = file.name.split('.').pop().toLowerCase();
        if (!['png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'].includes(ext)) return;
        if (file.size > 16 * 1024 * 1024) return;
        var reader = new FileReader();
        reader.onload = function (e) {
            if (imagePreview) imagePreview.src = e.target.result;
            if (previewContainer) previewContainer.style.display = 'flex';
            if (dropContent) dropContent.style.display = 'none';
            if (previewInfo) previewInfo.innerHTML = '<strong>' + file.name + '</strong> (' + (file.size / (1024 * 1024)).toFixed(2) + ' MB)';
            if (classifyBtn) classifyBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    function resetUpload() {
        if (fileInput) fileInput.value = '';
        if (imagePreview) imagePreview.src = '';
        if (previewContainer) previewContainer.style.display = 'none';
        if (dropContent) dropContent.style.display = 'block';
        if (classifyBtn) classifyBtn.disabled = true;
    }

    // ===== FORM SUBMIT LOADING STATE =====
    var uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function () {
            var btnText = document.getElementById('btnText');
            var btnLoader = document.getElementById('btnLoader');
            if (btnText) btnText.style.display = 'none';
            if (btnLoader) btnLoader.style.display = 'flex';
            if (classifyBtn) classifyBtn.disabled = true;
        });
    }

    // ===== SCROLL ANIMATIONS =====
    var animObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                entry.target.style.opacity = '1';
                animObs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.pipeline-card,.feature-card,.crop-card,.instruction-step').forEach(function (el, i) {
        el.style.opacity = '0';
        el.style.animationDelay = (i * 0.08) + 's';
        animObs.observe(el);
    });

    // ===== HERO PARTICLES (if any remain) =====
    var heroParticles = document.getElementById('heroParticles');
    if (heroParticles) {
        for (var i = 0; i < 25; i++) {
            var p = document.createElement('div');
            var size = Math.random() * 3 + 1;
            p.style.cssText = 'position:absolute;width:' + size + 'px;height:' + size + 'px;background:rgba(13,148,136,' + (Math.random() * 0.15 + 0.05) + ');border-radius:50%;left:' + Math.random() * 100 + '%;top:' + Math.random() * 100 + '%;animation:float ' + (Math.random() * 8 + 8) + 's ease-in-out infinite;animation-delay:' + (Math.random() * 5) + 's;';
            heroParticles.appendChild(p);
        }
    }

    // ===== SMOOTH SCROLL =====
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
        a.addEventListener('click', function (e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });    // ===== PREMIUM 3D SPACE SYSTEM =====
    if (document.getElementById('earth-container') && typeof THREE !== 'undefined') {
        const container = document.getElementById('earth-container');

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 20; // Moved back more
        camera.position.y = 0;  // Perfectly centered
        camera.position.x = 0;

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        // Earth Group
        const earthGroup = new THREE.Group();
        earthGroup.rotation.z = -23.4 * Math.PI / 180;
        scene.add(earthGroup);

        const textureLoader = new THREE.TextureLoader();
        textureLoader.crossOrigin = "Anonymous";

        // Load enhanced textures
        const earthMap = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg');
        const bumpMap = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');
        const specMap = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-water.png');
        const cloudMap = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-clouds.png');

        // Earth Mesh (Smaller & More Detailed)
        const geometry = new THREE.SphereGeometry(4, 64, 64);
        const material = new THREE.MeshPhongMaterial({
            map: earthMap,
            bumpMap: bumpMap,
            bumpScale: 0.18,
            specularMap: specMap,
            specular: new THREE.Color('#222'),
            shininess: 25
        });
        const earthMesh = new THREE.Mesh(geometry, material);
        earthGroup.add(earthMesh);

        // Clouds
        const cloudGeo = new THREE.SphereGeometry(4.06, 64, 64);
        const cloudMat = new THREE.MeshPhongMaterial({
            map: cloudMap,
            transparent: true,
            opacity: 0.35,
            blending: THREE.AdditiveBlending
        });
        const clouds = new THREE.Mesh(cloudGeo, cloudMat);
        earthGroup.add(clouds);

        // ===== REALISTIC SATELLITE (Orbiting around Earth) =====
        const orbitContainer = new THREE.Group();
        // Exact center orbit (Equator)
        orbitContainer.rotation.z = 0;
        orbitContainer.rotation.x = 0;

        // ===== MASTERPIECE SATELLITE (Sentinel-X Ultra) =====
        const satellite = new THREE.Group();

        // 1. Core Bus (Hexagonal Prism - Gold Foil)
        const coreGeo = new THREE.CylinderGeometry(0.5, 0.5, 1.6, 6);
        const coreMat = new THREE.MeshStandardMaterial({
            color: 0xffb700,
            roughness: 0.6,
            metalness: 1.0,
            flatShading: true // Faceted high-tech look
        });
        const core = new THREE.Mesh(coreGeo, coreMat);
        core.rotation.x = Math.PI / 2; // Lie along Z axis
        satellite.add(core);

        // 2. Armor Plating (Dark Titanium overlapping plates)
        for (let i = 0; i < 6; i++) {
            if (i % 2 === 0) {
                const panelGeo = new THREE.BoxGeometry(0.4, 0.08, 1.4);
                const panelMat = new THREE.MeshStandardMaterial({ color: 0x222222, metalness: 0.9, roughness: 0.2 });
                const panel = new THREE.Mesh(panelGeo, panelMat);
                const angle = i * Math.PI / 3;
                panel.position.set(Math.sin(angle) * 0.51, Math.cos(angle) * 0.51, 0);
                panel.rotation.z = -angle;
                satellite.add(panel);
            }
        }

        // 3. High-Resolution Optical Telescope (Pointing to -Y)
        const telescopeGroup = new THREE.Group();
        const tubeGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.8, 16);
        const tubeMat = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.9, roughness: 0.1 });
        const tube = new THREE.Mesh(tubeGeo, tubeMat);
        telescopeGroup.add(tube);

        const sunBaffleGeo = new THREE.CylinderGeometry(0.35, 0.3, 0.5, 16, 1, true); // Open sun shield
        const sunBaffleMat = new THREE.MeshStandardMaterial({ color: 0xeeeeee, metalness: 0.7, side: THREE.DoubleSide });
        const sunBaffle = new THREE.Mesh(sunBaffleGeo, sunBaffleMat);
        sunBaffle.position.y = -0.4;
        telescopeGroup.add(sunBaffle);

        const lensGeo = new THREE.SphereGeometry(0.28, 16, 16, 0, Math.PI);
        const lensMat = new THREE.MeshStandardMaterial({ color: 0x000510, metalness: 1.0, roughness: 0.0, transparent: true, opacity: 0.9 });
        const lens = new THREE.Mesh(lensGeo, lensMat);
        lens.position.y = -0.2;
        lens.rotation.x = Math.PI / 2;
        telescopeGroup.add(lens);

        telescopeGroup.position.y = -0.6; // Bottom of satellite
        satellite.add(telescopeGroup);

        // 4. Intricate Solar Arrays (Massive, multi-segmented)
        const panelGroup = new THREE.Group();
        satellite.userData.panelGroup = panelGroup; // For animation

        const boomGeo = new THREE.CylinderGeometry(0.04, 0.04, 4.0, 8);
        const boomMat = new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8 });
        const boom = new THREE.Mesh(boomGeo, boomMat);
        boom.rotation.z = Math.PI / 2; // Extend along X
        panelGroup.add(boom);

        const cellMat = new THREE.MeshStandardMaterial({ color: 0x020b24, metalness: 0.5, roughness: 0.1 });
        const frameMat = new THREE.MeshStandardMaterial({ color: 0xaaaaaa, metalness: 0.9, wireframe: true });

        [-1, 1].forEach(side => {
            [-1.1, 1.1].forEach(offset => {
                const wing = new THREE.Group();
                const cellGeo = new THREE.BoxGeometry(2.0, 0.04, 1.2);
                wing.add(new THREE.Mesh(cellGeo, cellMat));

                const frame = new THREE.Mesh(cellGeo, frameMat);
                frame.scale.set(1.01, 1.1, 1.01); // Slightly larger wireframe for grid effect
                wing.add(frame);

                wing.position.set(side * 2.5 + offset, 0, 0);
                panelGroup.add(wing);
            });
        });
        satellite.add(panelGroup);

        // 5. Advanced Communications Array (Radar Dish)
        const commsGroup = new THREE.Group();
        satellite.userData.commsGroup = commsGroup; // For animation

        const dishGeo = new THREE.SphereGeometry(0.4, 16, 16, 0, Math.PI, 0, Math.PI);
        const dishMat = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.3, side: THREE.DoubleSide, flatShading: true });
        const dish = new THREE.Mesh(dishGeo, dishMat);
        dish.rotation.x = -Math.PI / 2; // Face out
        commsGroup.add(dish);

        const receiverGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.3);
        const receiver = new THREE.Mesh(receiverGeo, tubeMat);
        receiver.position.z = 0.15;
        receiver.rotation.x = Math.PI / 2;
        commsGroup.add(receiver);

        commsGroup.position.set(0, 0.8, 0.5); // Top back
        satellite.add(commsGroup);

        // 6. Star Trackers (Navigation cones)
        const trackerGeo = new THREE.ConeGeometry(0.08, 0.25, 8);
        const tracker = new THREE.Mesh(trackerGeo, tubeMat);
        tracker.position.set(0.4, 0.4, -0.6);
        tracker.rotation.x = Math.PI / 4;
        tracker.rotation.z = -Math.PI / 4;
        satellite.add(tracker);

        // 7. Ion Thrusters (Glowing engine exhaust)
        const thrusterGroup = new THREE.Group();
        satellite.userData.thrusterPlumes = []; // For animation

        const engineGeo = new THREE.CylinderGeometry(0.12, 0.06, 0.25, 16);
        const engineMat = new THREE.MeshStandardMaterial({ color: 0x444444, metalness: 0.9 });

        [-0.25, 0.25].forEach(x => {
            const engine = new THREE.Mesh(engineGeo, engineMat);
            engine.position.set(x, 0, 0.8); // Back of satellite
            engine.rotation.x = Math.PI / 2;
            thrusterGroup.add(engine);

            // Sci-fi Blue Plasma Plume
            const plumeGeo = new THREE.ConeGeometry(0.1, 0.8, 16);
            const plumeMat = new THREE.MeshBasicMaterial({ color: 0x0088ff, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending });
            const plume = new THREE.Mesh(plumeGeo, plumeMat);
            plume.position.set(x, 0, 1.2);
            plume.rotation.x = -Math.PI / 2;
            thrusterGroup.add(plume);
            satellite.userData.thrusterPlumes.push(plume);
        });
        satellite.add(thrusterGroup);

        // 8. Ultra-Professional Holographic SAR/LiDAR Scanner
        const scannerGroup = new THREE.Group();

        // A. Holographic Scan Cone (Volumetric Laser)
        const coneGeo = new THREE.ConeGeometry(3.5, 12.0, 64, 1, true); // increased segments
        const coneMat = new THREE.MeshBasicMaterial({
            color: 0x00d4ff,
            transparent: true,
            opacity: 0.015, // Extremely subtle realistic haze
            blending: THREE.AdditiveBlending,
            side: THREE.DoubleSide,
            depthWrite: false
        });
        const scanCone = new THREE.Mesh(coneGeo, coneMat);

        // B. Data Matrix Wireframe (Very faint)
        const wireMat = new THREE.MeshBasicMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.03, // Barely visible high-tech grid
            wireframe: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        const scanWire = new THREE.Mesh(coneGeo, wireMat);

        const coneGroup = new THREE.Group();
        coneGroup.add(scanCone);
        coneGroup.add(scanWire);
        // Shift tip (y=6) to lens (-0.6). Base is at -12.6
        coneGroup.position.y = -6.6;
        scannerGroup.add(coneGroup);

        // C. Precision Laser Sweep Lines (Thin, sharp, realistic)
        const scanRings = [];
        for (let i = 0; i < 2; i++) {
            // Using a very thin ring for a sharp laser line effect
            const ringGeo = new THREE.RingGeometry(1.0, 1.02, 64);
            const ringMat = new THREE.MeshBasicMaterial({
                color: 0x00ffff,
                transparent: true,
                opacity: 0,
                side: THREE.DoubleSide,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = Math.PI / 2; // Flat
            scannerGroup.add(ring);
            scanRings.push({ mesh: ring, progress: i * 0.5 });
        }

        satellite.add(scannerGroup);
        satellite.userData.coneGroup = coneGroup;
        satellite.userData.coneMat = coneMat;
        satellite.userData.wireMat = wireMat;
        satellite.userData.scanRings = scanRings;

        // Scale satellite down so it looks realistic relative to Earth
        satellite.scale.set(0.12, 0.12, 0.12);

        // CRITICAL: Place satellite on the X-axis so it orbits around the Earth!
        satellite.position.set(5.5, 0, 0); // Closer to Earth (Earth is radius 4)

        // Rotate satellite so its bottom (-Y) points to Earth (-X)
        satellite.rotation.z = -Math.PI / 2;

        orbitContainer.add(satellite);
        scene.add(orbitContainer);

        // Realism: Pure Black Deep Space
        scene.background = new THREE.Color(0x000000);

        // Stars Layer (Deep & Distant)
        const starGeo = new THREE.BufferGeometry();
        const starCnt = 8000;
        const starArr = new Float32Array(starCnt * 3);
        for (let i = 0; i < starCnt * 3; i += 3) {
            starArr[i] = (Math.random() - 0.5) * 200;
            starArr[i + 1] = (Math.random() - 0.5) * 200;
            starArr[i + 2] = (Math.random() - 0.5) * 200;
        }
        starGeo.setAttribute('position', new THREE.BufferAttribute(starArr, 3));
        const starMat = new THREE.PointsMaterial({
            size: 0.08,
            color: 0xffffff,
            transparent: true,
            opacity: 0.7,
            blending: THREE.AdditiveBlending
        });
        const starField = new THREE.Points(starGeo, starMat);
        scene.add(starField);

        // Lighting
        const ambient = new THREE.AmbientLight(0xffffff, 0.2);
        scene.add(ambient);

        const sun = new THREE.DirectionalLight(0xffffff, 1.8);
        sun.position.set(20, 10, 15);
        scene.add(sun);

        function animate() {
            requestAnimationFrame(animate);
            const time = performance.now() * 0.0001;

            earthMesh.rotation.y += 0.0012;
            clouds.rotation.y += 0.0016;

            // Satellite orbiting slowly around the exact center
            orbitContainer.rotation.y += 0.005;

            // Ultra-realistic satellite animations
            if (satellite.userData.panelGroup) {
                // Panels slowly track the sun
                satellite.userData.panelGroup.rotation.x = Math.sin(time * 5) * 0.3;
            }
            if (satellite.userData.commsGroup) {
                // Radar dish sweeps for signal
                satellite.userData.commsGroup.rotation.y = Math.sin(time * 10) * 1.5;
            }
            if (satellite.userData.thrusterPlumes) {
                // Thrusters flicker like real plasma
                satellite.userData.thrusterPlumes.forEach(p => {
                    p.material.opacity = 0.5 + Math.random() * 0.5;
                    p.scale.y = 0.8 + Math.random() * 0.4;
                });
            }

            // Ultra-Professional Holographic Scan Animation
            if (satellite.userData.coneGroup) {
                // Spin the wireframe matrix rapidly
                satellite.userData.coneGroup.rotation.y -= 0.015;

                // Subtle pulse for realism
                satellite.userData.coneMat.opacity = 0.01 + Math.sin(time * 30) * 0.01;
                satellite.userData.wireMat.opacity = 0.02 + Math.sin(time * 30 + Math.PI) * 0.015;

                // Animate the sharp LiDAR sweep rings
                satellite.userData.scanRings.forEach(wave => {
                    wave.progress += 0.01; // Faster sharp scan
                    if (wave.progress > 1) wave.progress = 0;

                    // Move down from lens (-0.6) to earth surface (-12.6)
                    wave.mesh.position.y = -0.6 - (12.0 * wave.progress);

                    // Radius expands to match the cone (max radius 3.5 at bottom)
                    const currentScale = Math.max(0.01, 3.5 * wave.progress);
                    wave.mesh.scale.set(currentScale, currentScale, 1);

                    // Sharp laser pulse that fades smoothly but never gets too bright
                    // Max opacity is 0.35 for a realistic, professional look
                    wave.mesh.material.opacity = Math.pow(Math.sin(wave.progress * Math.PI), 4) * 0.35;
                });
            }

            starField.rotation.y += 0.0001;

            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    // ===== SATELLITE INTELLIGENCE HUB =====
    var globalSyncBtn = document.getElementById('globalSyncBtn');
    var intelGrid = document.getElementById('intelligenceGrid');
    var scanStatus = document.getElementById('scanStatus');

    if (globalSyncBtn && intelGrid) {
        globalSyncBtn.addEventListener('click', async function () {
            // UI State: Loading
            globalSyncBtn.disabled = true;
            globalSyncBtn.innerHTML = '<span class="spinner"></span> Analyzing Earth...';
            scanStatus.style.display = 'flex';

            try {
                const response = await fetch('/api/satellite/global-scan');
                const data = await response.json();

                // Clear grid
                intelGrid.innerHTML = '';

                // Populate Results
                data.regional_data.forEach(hub => {
                    const isDrought = hub.condition.includes('Drought');
                    const card = document.createElement('div');
                    card.className = 'intel-card animate-in';
                    card.innerHTML = `
                        <div class="intel-card-header">
                            <div>
                                <span class="intel-region">${hub.region}</span>
                                <h3 class="intel-crop">${hub.crop}</h3>
                            </div>
                            <span class="intel-icon">${isDrought ? '⚠️' : '🌱'}</span>
                        </div>
                        <div class="intel-metrics">
                            <div class="intel-metric">
                                <span class="metric-label">Rainfall</span>
                                <span class="metric-val">${hub.rainfall_estimate}</span>
                            </div>
                            <div class="intel-metric">
                                <span class="metric-label">Growth</span>
                                <span class="metric-val text-primary">${hub.growth_momentum}</span>
                            </div>
                            <div class="intel-metric">
                                <span class="metric-label">Moisture Index</span>
                                <span class="metric-val">${(hub.moisture_index * 100).toFixed(0)}%</span>
                            </div>
                            <div class="intel-metric">
                                <span class="metric-label">Loss Risk</span>
                                <span class="metric-val">${hub.biomass_loss}</span>
                            </div>
                        </div>
                        <div class="intel-condition ${isDrought ? 'condition-drought' : 'condition-healthy'}">
                            ${hub.condition}
                        </div>
                    `;
                    intelGrid.appendChild(card);
                });

                // Update stats banner in hero (optional)
                document.querySelector('.stat-item .stat-number[data-count="4"]').closest('.stat-item').innerHTML =
                    `<span class="stat-number">${data.optimal_growth_zones}</span><span class="stat-label">Growth Zones</span>`;

            } catch (error) {
                console.error('Satellite sync failed:', error);
                intelGrid.innerHTML = '<div class="intel-placeholder"><p>Failed to sync with Sentinel Hub. Please check your connection.</p></div>';
            } finally {
                globalSyncBtn.disabled = false;
                globalSyncBtn.innerHTML = '<span class="btn-icon">🌐</span> Global Sync Analysis';
                scanStatus.style.display = 'none';
            }
        });
    }

});
