document.addEventListener('DOMContentLoaded', () => {
    // Cache DOM references for 3D Parallax Portal (optimizes DOM performance)
    const scrollWrapper = document.querySelector('.parallax-scroll-wrapper');
    const layerCurtainLeft = document.querySelector('.layer-curtain-left');
    const layerCurtainRight = document.querySelector('.layer-curtain-right');
    const layerPortal = document.querySelector('.layer-portal');
    const layerBg = document.querySelector('.layer-bg');
    const parallaxScene = document.getElementById('parallax-scene');
    const beginBtn = document.querySelector('.hero-actions .btn-primary');
    const exploreBtn = document.querySelector('.hero-actions .btn-secondary');

    // Custom Cursor Glow Effect
    const cursorGlow = document.querySelector('.cursor-glow');
    
    document.addEventListener('mousemove', (e) => {
        requestAnimationFrame(() => {
            cursorGlow.style.left = `${e.clientX}px`;
            cursorGlow.style.top = `${e.clientY}px`;
        });
    });

    // Parallax Scroll Event Interpolation throttled with requestAnimationFrame
    let ticking = false;
    let scrollYVal = 0;

    const updateParallax = () => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            if (layerCurtainLeft) layerCurtainLeft.style.transform = '';
            if (layerCurtainRight) layerCurtainRight.style.transform = '';
            if (layerPortal) {
                layerPortal.style.transform = '';
                layerPortal.style.opacity = '';
            }
            if (layerBg) layerBg.style.transform = '';
            return;
        }
        const maxScroll = window.innerHeight;
        const progress = Math.min(scrollYVal / maxScroll, 1);
        
        // Split curtains left/right, scale portal ring, and scale space bg cleanly
        if (layerCurtainLeft) {
            layerCurtainLeft.style.transform = `translateX(${-progress * 100}%)`;
        }
        if (layerCurtainRight) {
            layerCurtainRight.style.transform = `translateX(${progress * 100}%)`;
        }
        if (layerPortal) {
            layerPortal.style.transform = `scale(${1 + progress * 2.5})`;
            layerPortal.style.opacity = `${1 - progress}`;
        }
        if (layerBg) {
            layerBg.style.transform = `scale(${1 + progress * 0.15})`;
        }
    };

    const onScroll = () => {
        scrollYVal = scrollWrapper ? scrollWrapper.scrollTop : window.scrollY;
        if (!ticking) {
            requestAnimationFrame(() => {
                updateParallax();
                ticking = false;
            });
            ticking = true;
        }
    };

    if (scrollWrapper) {
        scrollWrapper.addEventListener('scroll', onScroll);
    } else {
        window.addEventListener('scroll', onScroll);
    }

    // Consolidated Parallax Engine (compliant with Karpathy P6 Bloat Audit)
    // Immersive 3D Parallax & Gyroscopic Motion (Unified Single-Point of Truth)
    let parallaxRaf              = null;
    let currentParallaxX         = 0;
    let currentParallaxY         = 0;
    let targetParallaxX          = 0;
    let targetParallaxY          = 0;
    let activeParallaxMode       = null; // 'desktop' | 'mobile' | null
    let desktopMoveHandler       = null;
    let mobileOrientationHandler = null;
    let hasGyroPermission        = false;

    // ── Teardown (shared) ─────────────────────────────────────────────────────────
    const teardownParallax = () => {
        if (desktopMoveHandler) {
            document.removeEventListener('mousemove', desktopMoveHandler);
            desktopMoveHandler = null;
        }
        if (mobileOrientationHandler) {
            window.removeEventListener('deviceorientation', mobileOrientationHandler);
            mobileOrientationHandler = null;
        }
        if (parallaxRaf) {
            cancelAnimationFrame(parallaxRaf);
            parallaxRaf = null;
        }
        // Reset interpolation state so next init starts from rest
        currentParallaxX = 0;
        currentParallaxY = 0;
        targetParallaxX  = 0;
        targetParallaxY  = 0;
        activeParallaxMode = null;
    };

    // ── Main init (called on load + on every resize crossing 768px) ───────────────
    const initAdaptiveParallax = () => {
        const scene = document.getElementById('parallax-scene');
        if (!scene) return;

        const isMobile = window.innerWidth < 768;
        teardownParallax(); // always clean before reinit

        if (!isMobile) {
            // ── DESKTOP: mouse-tilt (rotation) ──────────────────────────────────
            activeParallaxMode = 'desktop';

            desktopMoveHandler = (e) => {
                const cx = window.innerWidth  / 2;
                const cy = window.innerHeight / 2;
                // Clamp to ±5 degrees — prevents edge-clipping at extreme cursor positions
                targetParallaxX = Math.max(-5, Math.min(5, ((e.clientX - cx) / cx) * 5));
                targetParallaxY = Math.max(-5, Math.min(5, ((e.clientY - cy) / cy) * 5));
            };
            document.addEventListener('mousemove', desktopMoveHandler);

            const updateDesktop = () => {
                if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                    scene.style.transform = '';
                    parallaxRaf = requestAnimationFrame(updateDesktop);
                    return;
                }
                // LERP factor 0.08 — holographic "heavy panel" feel
                currentParallaxX += (targetParallaxX - currentParallaxX) * 0.08;
                currentParallaxY += (targetParallaxY - currentParallaxY) * 0.08;
                scene.style.transform =
                    `perspective(800px) rotateY(${currentParallaxX}deg) rotateX(${-currentParallaxY}deg)`;
                parallaxRaf = requestAnimationFrame(updateDesktop);
            };
            parallaxRaf = requestAnimationFrame(updateDesktop);

        } else {
            // ── MOBILE: gyroscope (translation, not rotation) ────────────────────
            // Translation prevents rounded-corner edge-clipping on phone frame mockup.
            activeParallaxMode = 'mobile';

            mobileOrientationHandler = (e) => {
                const beta  = e.beta;   // tilt front-to-back  [-180, 180]
                const gamma = e.gamma;  // tilt left-to-right  [-90, 90]
                if (beta === null || gamma === null) return;
                // 45° vertical = comfortable phone-holding reference
                const rawX = Math.max(-15, Math.min(15, gamma));
                const rawY = Math.max(-15, Math.min(15, beta - 45));
                // Map ±15° range → ±8px translation
                targetParallaxX = (rawX / 15) * 8;
                targetParallaxY = (rawY / 15) * 8;
            };

            const startListeningGyro = () => {
                // Guard against double-binding on repeated calls
                window.removeEventListener('deviceorientation', mobileOrientationHandler);
                window.addEventListener('deviceorientation', mobileOrientationHandler);

                const updateMobile = () => {
                    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                        scene.style.transform = '';
                        parallaxRaf = requestAnimationFrame(updateMobile);
                        return;
                    }
                    // Low-pass filter — eliminates high-frequency gyro jitter
                    currentParallaxX = currentParallaxX * 0.85 + targetParallaxX * 0.15;
                    currentParallaxY = currentParallaxY * 0.85 + targetParallaxY * 0.15;
                    scene.style.transform =
                        `translate3d(${currentParallaxX}px, ${currentParallaxY}px, 0)`;
                    parallaxRaf = requestAnimationFrame(updateMobile);
                };
                parallaxRaf = requestAnimationFrame(updateMobile);
            };

            // iOS 13+ requires permission from a user gesture handler.
            // window.requestGyroPermission is called from triggerFabricDemo(),
            // beginBtn click, and exploreBtn click — all tap/click handlers.
            window.requestGyroPermission = async () => {
                if (
                    typeof DeviceOrientationEvent !== 'undefined' &&
                    typeof DeviceOrientationEvent.requestPermission === 'function'
                ) {
                    // iOS 13+ path
                    try {
                        const response = await DeviceOrientationEvent.requestPermission();
                        if (response === 'granted') {
                            hasGyroPermission = true;
                            startListeningGyro();
                        }
                        // Denied: graceful no-op — portal continues working without tilt
                    } catch (error) {
                        console.warn('Gyro permission request failed:', error);
                    }
                } else {
                    // Android / non-iOS: no permission API, start immediately
                    startListeningGyro();
                }
            };

            // Auto-start if permission was already granted in this session
            // (e.g. user navigated away and back without closing the tab)
            if (
                hasGyroPermission ||
                (
                    typeof DeviceOrientationEvent !== 'undefined' &&
                    typeof DeviceOrientationEvent.requestPermission !== 'function'
                )
            ) {
                startListeningGyro();
            }
        }
    };

    // Run adaptive parallax on initial load
    initAdaptiveParallax();

    const requestGyroPermissionOnGesture = () => {
        if (window.requestGyroPermission) {
            window.requestGyroPermission();
        }
    };

    if (beginBtn) beginBtn.addEventListener('click', requestGyroPermissionOnGesture);
    if (exploreBtn) exploreBtn.addEventListener('click', requestGyroPermissionOnGesture);

    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Reveal Animations on Scroll
    const revealElements = document.querySelectorAll('.reveal');

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        const elementVisible = 100;

        revealElements.forEach((element) => {
            const elementTop = element.getBoundingClientRect().top;
            if (elementTop < windowHeight - elementVisible) {
                element.classList.add('active');
            }
        });
    };

    // Initial check
    revealOnScroll();
    
    // Check on scroll
    window.addEventListener('scroll', revealOnScroll);

    // Holographic Tilt Effect for Cards
    const tiltCards = document.querySelectorAll('.stat-card, .glass-card');
    tiltCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px) scale(1.02)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0) scale(1)';
        });
    });

    // Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if(targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // 3D Knowledge Graph Initialization with Self-Healing Retry
    const init3DGraph = () => {
        const graphContainer = document.getElementById('3d-graph-container');
        if (!graphContainer) return;

        if (typeof ForceGraph3D === 'undefined') {
            console.warn("ForceGraph3D is not loaded yet. Retrying in 200ms...");
            setTimeout(init3DGraph, 200);
            return;
        }

        console.log("ForceGraph3D loaded. Initializing premium 3D neural map...");

        const graphData = {
            nodes: [
                // Core
                { id: 'MCT', group: 1, val: 25, name: 'Microsoft Certified Trainer (MCT)' },
                
                // Ecosystems & Platforms
                { id: 'Azure Data Ecosystem', group: 2, val: 18, name: 'Azure Data Ecosystem' },
                { id: 'Microsoft Fabric', group: 3, val: 20, name: 'Microsoft Fabric' },
                { id: 'Azure Databricks', group: 3, val: 18, name: 'Azure Databricks' },
                { id: 'Power BI', group: 6, val: 18, name: 'Power BI Ecosystem' },
                
                // Architecture & Concepts
                { id: 'Medallion Architecture', group: 4, val: 15, name: 'Medallion Architecture' },
                { id: 'Lakehouse', group: 4, val: 12, name: 'Lakehouse Pattern' },
                { id: 'Data Mesh', group: 4, val: 12, name: 'Data Mesh Strategy' },
                
                // Certifications
                { id: 'DP-700', group: 5, val: 18, name: 'DP-700: Microsoft Fabric Data Engineer (Active)' },
                { id: 'DP-600', group: 5, val: 15, name: 'DP-600: Fabric Analytics Engineer (Active)' },
                { id: 'DP-203', group: 5, val: 15, name: 'DP-203: Azure Data Engineer (Retired)' },
                { id: 'DP-900', group: 5, val: 10, name: 'DP-900: Azure Data Fundamentals (Coming Soon)' },
                
                // Specific Technologies & Modules
                { id: 'ADLS Gen2', group: 2, val: 10, name: 'ADLS Gen2 Storage' },
                { id: 'Event Hub', group: 2, val: 10, name: 'Azure Event Hubs' },
                { id: 'Key Vault', group: 2, val: 8, name: 'Azure Key Vault' },
                { id: 'PySpark', group: 3, val: 12, name: 'PySpark / Spark SQL' },
                { id: 'Delta Lake', group: 4, val: 12, name: 'Delta Lake Tables' },
                { id: 'DAX', group: 6, val: 10, name: 'DAX Optimization' },
                { id: 'Alteryx', group: 7, val: 12, name: 'Alteryx Workflows' },
                { id: 'Python Automation', group: 7, val: 14, name: 'Python Automation' },
                { id: 'Global Enterprise Cohorts', group: 8, val: 16, name: 'Global Enterprise Upskilling' }
            ],
            links: [
                { source: 'MCT', target: 'Azure Data Ecosystem' },
                { source: 'MCT', target: 'Microsoft Fabric' },
                { source: 'MCT', target: 'DP-700' },
                { source: 'MCT', target: 'DP-600' },
                { source: 'MCT', target: 'DP-203' },
                { source: 'MCT', target: 'DP-900' },
                { source: 'MCT', target: 'Global Enterprise Cohorts' },
                
                { source: 'Azure Data Ecosystem', target: 'Azure Databricks' },
                { source: 'Azure Data Ecosystem', target: 'ADLS Gen2' },
                { source: 'Azure Data Ecosystem', target: 'Event Hub' },
                { source: 'Azure Data Ecosystem', target: 'Key Vault' },
                
                { source: 'Microsoft Fabric', target: 'Medallion Architecture' },
                { source: 'Microsoft Fabric', target: 'Lakehouse' },
                { source: 'Microsoft Fabric', target: 'Power BI' },
                { source: 'Microsoft Fabric', target: 'DP-700' },
                { source: 'Microsoft Fabric', target: 'DP-600' },
                
                { source: 'Azure Databricks', target: 'Medallion Architecture' },
                { source: 'Azure Databricks', target: 'PySpark' },
                { source: 'Azure Databricks', target: 'Delta Lake' },
                
                { source: 'Lakehouse', target: 'Delta Lake' },
                { source: 'Medallion Architecture', target: 'Data Mesh' },
                
                { source: 'Power BI', target: 'DAX' },
                { source: 'Power BI', target: 'Alteryx' }, // Showing data prep connection
                
                { source: 'Python Automation', target: 'Alteryx' },
                { source: 'Python Automation', target: 'Azure Databricks' },
                
                { source: 'DP-700', target: 'Microsoft Fabric' },
                { source: 'DP-700', target: 'Global Enterprise Cohorts' },
                { source: 'DP-203', target: 'Azure Data Ecosystem' },
                { source: 'DP-900', target: 'Global Enterprise Cohorts' },
                { source: 'DP-600', target: 'Global Enterprise Cohorts' },
                { source: 'DP-203', target: 'Global Enterprise Cohorts' }
            ]
        };

        // Color palette matching the Cosmic Gold / Neon Blue theme
        const groupColors = {
            1: '#FFD700', // Cosmic Gold (MCT)
            2: '#00F3FF', // Neon Blue (Azure)
            3: '#8A2BE2', // Deep Purple (Fabric/Databricks)
            4: '#00FA9A', // Spring Green (Architecture)
            5: '#FF8C00', // Dark Orange (Certifications)
            6: '#F0E68C', // Khaki (Power BI)
            7: '#FF1493', // Deep Pink (Automation)
            8: '#FFF8DC'  // Cornsilk (Global Cohorts)
        };

        const Graph = ForceGraph3D()(graphContainer)
            .graphData(graphData)
            .nodeLabel('name')
            .nodeColor(node => groupColors[node.group] || '#ffffff')
            .nodeVal(node => node.val)
            .nodeRelSize(3) // Adjusted baseline size for dynamic nodeVal scaling
            .linkColor(link => {
                const sourceGroup = typeof link.source === 'object' ? link.source.group : graphData.nodes.find(n => n.id === link.source).group;
                return groupColors[sourceGroup] + 'A0'; // Add 62% opacity for higher visibility
            })
            .linkWidth(2.0) // Thicker links for dynamic tesseract lines
            .linkDirectionalParticles(3) // Energy particles moving between dimensions
            .linkDirectionalParticleSpeed(0.007)
            .linkDirectionalParticleWidth(3.0)
            .linkOpacity(0.55)
            .backgroundColor('rgba(5, 7, 15, 0.35)') // Dark translucent background to enhance contrast
            .showNavInfo(false)
            .onNodeHover(node => graphContainer.style.cursor = node ? 'pointer' : null);

        // Auto-rotate
        let angle = 0;
        const rotationInterval = setInterval(() => {
            if (!document.getElementById('3d-graph-container')) {
                clearInterval(rotationInterval);
                return;
            }
            Graph.cameraPosition({
                x: 220 * Math.sin(angle),
                z: 220 * Math.cos(angle)
            });
            angle += Math.PI / 450; // smooth slow-motion tesseract rotation
        }, 30);

        // Resize handler
        window.addEventListener('resize', () => {
            Graph.width(graphContainer.clientWidth);
            Graph.height(graphContainer.clientHeight);
        });

        // Link Graph Node Clicks to AI Assistant
        Graph.onNodeClick(node => {
            openAssistant();
            const prompt = `Tell me more about ${node.name}. What is its role in Microsoft Fabric and the Nth Dimension?`;
            addMessage('user', prompt);
            callNIM(prompt);
        });
    };

    // Run the initialization
    init3DGraph();

    // AI Assistant Logic
    const aiAssistant = document.getElementById('ai-assistant');
    const openBtn = document.getElementById('open-assistant');
    const closeBtn = document.getElementById('close-assistant');
    const sendBtn = document.getElementById('send-msg');
    const voiceBtn = document.getElementById('voice-msg');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    let chatHistory = [];

    const openAssistant = () => {
        aiAssistant.classList.remove('hidden');
        openBtn.style.display = 'none';
    };

    const closeAssistant = () => {
        aiAssistant.classList.add('hidden');
        openBtn.style.display = 'flex';
    };

    const addMessage = (role, text) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.innerHTML = `<p>${text}</p>`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const callNIM = async (text) => {
        try {
            // Show Thinking state
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'message system thinking';
            thinkingDiv.innerHTML = '<p><i class="ph ph-sparkle"></i> The Guide is consulting the Nth Dimension...</p>';
            chatMessages.appendChild(thinkingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, history: chatHistory })
            });
            
            // Remove Thinking state
            thinkingDiv.remove();

            const data = await response.json();
            
            // Parse for Actions
            const actionMatch = data.response.match(/\[ACTION:(.*?)\]/);
            if (actionMatch) {
                const action = actionMatch[1];
                handleUIAction(action);
                const cleanResponse = data.response.replace(/\[ACTION:.*?\]/g, '').trim();
                addMessage('system', cleanResponse);
            } else {
                addMessage('system', data.response);
            }

            chatHistory.push({ role: 'user', content: text });
            chatHistory.push({ role: 'assistant', content: data.response });
        } catch (error) {
            console.error('NIM Error:', error);
            const thinking = chatMessages.querySelector('.thinking');
            if(thinking) thinking.remove();
            addMessage('system', "Apologies, Voyager. The dimensional link is unstable. Please ensure the backend is running.");
        }
    };

    const handleUIAction = (action) => {
        console.log("Triggering Action:", action);
        switch(action) {
            case 'SCROLL_TO_EXPERTISE':
                document.getElementById('expertise').scrollIntoView({ behavior: 'smooth' });
                break;
            case 'SCROLL_TO_FABRIC':
            case 'PLAY_VIDEO_FABRIC':
                document.getElementById('fabric-demo').scrollIntoView({ behavior: 'smooth' });
                // Add highlight effect
                document.querySelector('.demo-container').classList.add('neon-pulse');
                setTimeout(() => document.querySelector('.demo-container').classList.remove('neon-pulse'), 3000);
                break;
            case 'BOOK_MEETING':
                window.open('mailto:mct@nthdimensionacademy.com?subject=Inquiry from Nth Dimension Academy', '_blank');
                break;
            default:
                console.warn("Unknown action:", action);
        }
    };

    window.triggerFabricDemo = () => {
        const isMobile = window.innerWidth < 768;
        const video169 = document.getElementById('fabric-video-16-9');
        const video916 = document.getElementById('fabric-video-9-16');
        const overlay = document.getElementById('demo-overlay');
        
        const activeVideo = isMobile ? video916 : video169;
        const inactiveVideo = isMobile ? video169 : video916;
        
        if (inactiveVideo) {
            inactiveVideo.pause();
        }
        
        if (activeVideo) {
            if (overlay) overlay.style.display = 'none';
            activeVideo.controls = true;
            activeVideo.play().catch(error => {
                console.warn("Play blocked or interrupted:", error);
                if (overlay) overlay.style.display = 'flex';
            });
        }

        // Trigger mobile gyroscope permission check if available
        if (isMobile && window.requestGyroPermission) {
            window.requestGyroPermission();
        }

        openAssistant();
        addMessage('system', "Initiating N<span class='nth-style'>TH</span> Dimension Fabric Demo Masterclass... Observe the convergence of data streams.");
        const demoPrompt = "I am watching the Microsoft Fabric Demo. Explain the key architectural components being shown and how they align with the NTH Dimension.";
        addMessage('user', "Launch the Fabric Demo.");
        callNIM(demoPrompt);
        
        const demoContainer = document.querySelector('.demo-container');
        if (demoContainer) {
            demoContainer.classList.add('neon-pulse');
            setTimeout(() => demoContainer.classList.remove('neon-pulse'), 5000);
        }
    };

    // Debounced Resize handler to pause and reset videos on crossing breakpoint, and adjust parallax
    let resizeTimeout;
    let wasMobile = window.innerWidth < 768;

    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const isMobileNow = window.innerWidth < 768;
            if (isMobileNow !== wasMobile) {
                // Breakpoint crossed! Pause all videos and reset overlay
                const video169 = document.getElementById('fabric-video-16-9');
                const video916 = document.getElementById('fabric-video-9-16');
                const overlay = document.getElementById('demo-overlay');

                if (video169) {
                    video169.pause();
                    video169.controls = false;
                }
                if (video916) {
                    video916.pause();
                    video916.controls = false;
                }
                if (overlay) {
                    overlay.style.display = 'flex';
                }
                wasMobile = isMobileNow;
                
                // Re-evaluate parallax modules
                initAdaptiveParallax();
                
                console.log("Viewport breakpoint crossed. Paused playback, reset player state, and switched 3D parallax mode.");
            }
        }, 200);
    });

    const synthesizeVoice = async (text) => {
        try {
            addMessage('system', "Synthesizing voice in the Nth Dimension...");
            const response = await fetch('http://localhost:8000/api/voice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, target_language: "te-IN" }) // Default to Telugu as per Multilingual Tutor goal
            });
            const data = await response.json();
            if (data.audio_urls) {
                const audio = new Audio(data.audio_urls[0]);
                audio.play();
            }
        } catch (error) {
            console.error('Voice Error:', error);
        }
    };

    openBtn.addEventListener('click', openAssistant);
    closeBtn.addEventListener('click', closeAssistant);

    sendBtn.addEventListener('click', () => {
        const text = userInput.value.trim();
        if (text) {
            addMessage('user', text);
            userInput.value = '';
            callNIM(text);
        }
    });

    voiceBtn.addEventListener('click', () => {
        const lastMessage = Array.from(chatMessages.querySelectorAll('.message.system p')).pop();
        if (lastMessage) {
            synthesizeVoice(lastMessage.innerText);
        }
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendBtn.click();
    });

    // Video Carousel Swiping & Clickable Dots Interaction
    const carousel = document.querySelector('.video-carousel');
    const dots = document.querySelectorAll('.carousel-dot');

    if (carousel && dots.length > 0) {
        carousel.addEventListener('scroll', () => {
            const index = Math.round(carousel.scrollLeft / carousel.clientWidth);
            dots.forEach((dot, idx) => {
                if (idx === index) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        });

        dots.forEach(dot => {
            dot.addEventListener('click', function() {
                const targetIndex = parseInt(this.getAttribute('data-index'));
                carousel.scrollTo({
                    left: targetIndex * carousel.clientWidth,
                    behavior: 'smooth'
                });
            });
        });
    }
    // Detailed Syllabus Data for Dynamic Modal Injection
    const syllabusData = {
        dp700: {
            trustPill: "DP-700 MASTER CURRICULUM",
            title: "Microsoft Fabric Data Engineer Atlas",
            status: "active",
            statusText: "Active",
            exam: "Exam DP-700",
            credential: "Fabric Data Engineer Associate",
            level: "Elite Master",
            cost: "$165 USD",
            weights: [
                { topic: "Implement & Manage Analytics Solution", weight: "30–35%" },
                { topic: "Ingest & Transform Data", weight: "30–35%" },
                { topic: "Monitor & Optimize Analytics Solution", weight: "30–35%" }
            ],
            description: [
                "Led by Master Consultant and Microsoft Certified Trainer (MCT) <strong>Navakanth Reddy Dumpa</strong>, this curriculum is engineered to guide data professionals through the architectural and operational realities of the unified Microsoft Fabric ecosystem.",
                "Perfect for intermediate and advanced data professionals seeking to master batch pipelines, lakehouse medallion architectures, database mirroring, OneLake virtualization, real-time intelligence streams, and version control (CI/CD DevOps)."
            ],
            tracks: [
                {
                    title: "🛠️ Track 1: Workspace Management, Security & CI/CD",
                    desc: "Capacity governance, custom Spark compute pools, Azure DevOps version control, Row-Level (RLS) & Column-Level Security (CLS), and multi-stage deployment release pipelines."
                },
                {
                    title: "💾 Track 2: OneLake Architecture & Medallion Strategy",
                    desc: "Designing high-performance Delta Parquet tables, conformed schema processing, and establishing structured Medallion pipelines (Bronze ➔ Silver ➔ Gold) within Lakehouses."
                },
                {
                    title: "🚀 Track 3: High-Scale Ingestion & Mirroring",
                    desc: "Ingestion pipelines, Dataflows Gen2, OneLake cloud shortcuts (S3, ADLS Gen2, GCS) with zero sync delay, and continuous database replication (Mirroring) from SQL / Snowflake."
                },
                {
                    title: "💻 Track 4: Advanced Multi-Engine Transformations",
                    desc: "PySpark Notebook processing at scale, T-SQL Synapse Warehouse engineering, views, stored procedures, and Kusto Query Language (KQL) analytics."
                },
                {
                    title: "📡 Track 5: Real-Time Intelligence & Streaming Analytics",
                    desc: "Eventstreams, Eventhouses, KQL databases, CDC event routing, and streaming window transformations (sliding, session, tumbling)."
                }
            ],
            labs: [
                {
                    num: "LAB 01",
                    title: "Create and Configure a Fabric Lakehouse",
                    desc: "Provision spaces, import historical structured sales datasets, build PySpark Delta Tables, and run analytics queries via SQL endpoints."
                },
                {
                    num: "LAB 02",
                    title: "Orchestrate Batch Ingestion with Pipelines",
                    desc: "Construct data pipeline copy activities, parameterize SQL database sources, and chain automated notebooks and trigger alerts."
                },
                {
                    num: "LAB 03",
                    title: "No-Code ETL with Dataflows Gen2",
                    desc: "Leverage visual Power Query Online to clean profiles, replace null fields, and load conformed dimensions."
                },
                {
                    num: "LAB 04",
                    title: "Advanced Transformations using Spark Notebooks",
                    desc: "Perform large-scale joins, deduplication, timestamp formatting, and partition output Delta tables in OneLake dynamically."
                },
                {
                    num: "LAB 05",
                    title: "Delta Lake Optimization & Time Travel",
                    desc: "Query transaction history logs using versionAsOf, and execute performance optimization commands (OPTIMIZE, Z-ORDER, VACUUM)."
                },
                {
                    num: "LAB 06",
                    title: "Implement and Load a Synapse Data Warehouse",
                    desc: "Create an enterprise data warehouse, load dimension tables using T-SQL, and run cross-database queries."
                },
                {
                    num: "LAB 07",
                    title: "Set Up Real-Time Eventstreams and KQL",
                    desc: "Ingest real-time simulator telemetry data, configure event processors, design Eventhouses, and query streams using KQL querysets."
                },
                {
                    num: "LAB 08",
                    title: "Implement Security, Governance & CI/CD",
                    desc: "Secure data fields (RLS/CLS), track Purview metadata, link workspaces to Git Azure DevOps, and construct release pipelines."
                }
            ]
        },
        dp600: {
            trustPill: "DP-600 MASTER CURRICULUM",
            title: "Microsoft Fabric Analytics Engineer Atlas",
            status: "active",
            statusText: "Active",
            exam: "Exam DP-600",
            credential: "Fabric Analytics Engineer Associate",
            level: "Specialist",
            cost: "$165 USD",
            weights: [
                { topic: "Plan & Implement Analytics Env", weight: "10–15%" },
                { topic: "Prepare & Serve Data", weight: "40–45%" },
                { topic: "Implement & Manage Semantic Models", weight: "25–30%" },
                { topic: "Explore & Analyze Data", weight: "20–25%" }
            ],
            description: [
                "Led by Master Consultant and Microsoft Certified Trainer (MCT) <strong>Navakanth Reddy Dumpa</strong>, this curriculum is designed to guide analytics professionals from core SQL/Power BI development into the architectural realities of the unified Microsoft Fabric ecosystem.",
                "Perfect for intermediate and advanced analytics professionals seeking to master data preparation, Star Schema modeling, advanced DAX programming, Direct Lake mode optimization, and version control (CI/CD DevOps)."
            ],
            tracks: [
                {
                    title: "🛠️ Track 1: Tenant & Workspace Administration, Security & Git",
                    desc: "Capacity governance, tenant settings, custom Spark pools, Azure DevOps Git integration, row/column/object-level security, and multi-stage deployment release pipelines."
                },
                {
                    title: "💾 Track 2: OneLake Data Warehousing & Medallion Strategy",
                    desc: "OneLake logical unified layout, Delta Parquet tables, conformed schema processing, and establishing structured Medallion pipelines (Bronze ➔ Silver ➔ Gold) within Data Warehouses."
                },
                {
                    title: "🚀 Track 3: Data Ingestion, Mirroring & Virtualization",
                    desc: "Harness Data Factory Pipelines, Dataflows Gen2, database Mirroring, and OneLake shortcuts (S3, ADLS Gen2, GCS) with zero sync delay."
                },
                {
                    title: "💻 Track 4: Advanced Multi-Engine Transformations",
                    desc: "PySpark Notebook processing at scale, T-SQL Synapse Warehouse engineering, views, stored procedures, and Kusto Query Language (KQL) analytics."
                },
                {
                    title: "📡 Track 5: Real-Time Intelligence & Streaming Analytics",
                    desc: "Eventstreams, Eventhouses, KQL databases, CDC event routing, and streaming window transformations (sliding, session, tumbling)."
                }
            ],
            labs: [
                {
                    num: "LAB 01",
                    title: "Create and Configure a Fabric Lakehouse",
                    desc: "Provision spaces, import historical sales datasets, build PySpark Delta tables, and query via SQL endpoints."
                },
                {
                    num: "LAB 02",
                    title: "Orchestrate Batch Ingestion with Pipelines",
                    desc: "Construct data pipeline copy activities, parameterize SQL database sources, and chain automated notebooks and trigger alerts."
                },
                {
                    num: "LAB 03",
                    title: "No-Code ETL with Dataflows Gen2",
                    desc: "Leverage visual Power Query Online to clean profiles, replace null fields, and load conformed dimensions."
                },
                {
                    num: "LAB 04",
                    title: "Advanced Transformations using Spark Notebooks",
                    desc: "Perform large-scale joins, deduplication, timestamp formatting, and partition output Delta tables in OneLake dynamically."
                },
                {
                    num: "LAB 05",
                    title: "Delta Lake Optimization & Time Travel",
                    desc: "Query transaction history logs using versionAsOf, and execute performance optimization commands (OPTIMIZE, Z-ORDER, VACUUM)."
                },
                {
                    num: "LAB 06",
                    title: "Implement and Load a Synapse Data Warehouse",
                    desc: "Create an enterprise data warehouse, load dimension tables using T-SQL, and run cross-database queries."
                },
                {
                    num: "LAB 07",
                    title: "Set Up Real-Time Eventstreams and KQL",
                    desc: "Ingest real-time simulator telemetry data, configure event processors, design Eventhouses, and query streams using KQL querysets."
                },
                {
                    num: "LAB 08",
                    title: "Implement Security, Governance & CI/CD",
                    desc: "Secure data fields (RLS/CLS), track Purview metadata, link workspaces to Git Azure DevOps, and construct release pipelines."
                }
            ]
        },
        dp900: {
            trustPill: "DP-900 CURRICULUM",
            title: "Azure Data Fundamentals (Coming Soon)",
            status: "coming",
            statusText: "Coming Soon",
            exam: "Exam DP-900",
            credential: "Microsoft Certified: Azure Data Fundamentals",
            level: "Foundation",
            cost: "$99 USD",
            weights: [
                { topic: "Describe Core Data Concepts", weight: "25–30%" },
                { topic: "Identify Relational Data on Azure", weight: "20–25%" },
                { topic: "Identify Non-Relational Data on Azure", weight: "15–20%" },
                { topic: "Describe Analytics Workloads on Azure", weight: "25–30%" }
            ],
            description: [
                "Led by Master Consultant and Microsoft Certified Trainer (MCT) <strong>Navakanth Reddy Dumpa</strong>, this foundational course is tailored to establish a rock-solid baseline in modern cloud databases, relational and non-relational storage configurations, and fundamental business intelligence pipelines.",
                "<strong>Syllabus Status:</strong> Under active development and coming extremely soon! Get priority notifications and early access sandbox resources as soon as it launches."
            ],
            tracks: [
                {
                    title: "📚 Track 1: Core Cloud Data Fundamentals",
                    desc: "Explore structured, semi-structured, and unstructured database schemas. Understand relational database properties, ACID rules, and basic analytics roles."
                },
                {
                    title: "🔍 Track 2: Relational Databases on Azure",
                    desc: "Analyze relational server offerings including Azure SQL Database, SQL Managed Instance, Azure Cosmos DB for PostgreSQL, and relational query tools."
                },
                {
                    title: "💾 Track 3: Non-Relational Storage Models",
                    desc: "Understand NoSQL structures, Azure Blob Storage, Azure Files, ADLS Gen2, and Cosmos DB API models (SQL, MongoDB, Cassandra, Graph)."
                },
                {
                    title: "📊 Track 4: Analytics Workloads & Synapse",
                    desc: "Foundations of data warehousing, star schemas, dimensional modeling, and modern ELT orchestrations using Azure Synapse Analytics."
                }
            ],
            labs: [
                {
                    num: "LAB 01",
                    title: "Provision and Query an Azure SQL Database",
                    desc: "Create an active Azure SQL Database resource, configure workspace firewalls, and execute basic DDL/DML SELECT commands using standard T-SQL."
                },
                {
                    num: "LAB 02",
                    title: "NoSQL Database Provisioning with Cosmos DB",
                    desc: "Create an Azure Cosmos DB database account, insert JSON document records, and query NoSQL datasets."
                },
                {
                    num: "LAB 03",
                    title: "Ingestion and Orchestration in Azure Synapse",
                    desc: "Provision Synapse spaces, configure Synapse pipelines to ingest Blob data, and load curated tables."
                }
            ]
        },
        dp203: {
            trustPill: "DP-203 RETIRED CURRICULUM",
            title: "Azure Data Engineering Legacy",
            status: "retired",
            statusText: "Retired",
            exam: "Exam DP-203",
            credential: "Microsoft Certified: Azure Data Engineer Associate",
            level: "Legacy Core",
            cost: "$165 USD",
            weights: [
                { topic: "Design & Implement Data Storage", weight: "40–45%" },
                { topic: "Develop Data Processing", weight: "25–30%" },
                { topic: "Secure, Monitor & Optimize Data Storage", weight: "30–35%" }
            ],
            description: [
                "Led by Master Consultant and Microsoft Certified Trainer (M MCT) <strong>Navakanth Reddy Dumpa</strong>, this legacy curriculum was highly successful, helping hundreds of engineers master Azure Databricks, Azure Synapse Analytics, and Azure Data Factory pipelines.",
                "<strong>Syllabus Status:</strong> This course is now retired as Microsoft Fabric (DP-700 / DP-600) transitions organizations to a unified SaaS lakehouse paradigm. However, the foundational modules are kept here for historical reference."
            ],
            tracks: [
                {
                    title: "💾 Track 1: Data Storage & Infrastructure Architectures",
                    desc: "Implement partition schemes, configure ADLS Gen2 directory hierarchies, and design premium security layers inside Azure Synapse dedicated SQL pools."
                },
                {
                    title: "⚙️ Track 2: Large-Scale PySpark Transformation",
                    desc: "Develop advanced spark transformations using Databricks notebooks, manage DBFS storage options, optimize cluster configurations, and manage delta tables."
                },
                {
                    title: "🚀 Track 3: Batch and Streaming Pipelines",
                    desc: "Build hybrid batch loading patterns using Azure Data Factory pipelines, integrate Azure Key Vault secrets, and process streaming data with Azure Stream Analytics."
                }
            ],
            labs: [
                {
                    num: "LAB 01",
                    title: "Azure Databricks Data Wrangling at Scale",
                    desc: "Create clusters, load massive CSV files, apply schemas, and clean columns using high-performance Spark SQL operations."
                },
                {
                    num: "LAB 02",
                    title: "Build Synapse Dedicated SQL Pool Warehouses",
                    desc: "Design hash-distributed and replicated dimension tables, partition fact tables, and execute COPY statements for fast loading."
                },
                {
                    num: "LAB 03",
                    title: "Deploy End-to-End Orchestrated pipelines in ADF",
                    desc: "Construct parameterized pipelines, map copy data activities, and configure self-hosted integration runtimes."
                }
            ]
        }
    };

    let currentSyllabusCourseId = 'dp700';

    // Global functions for Syllabus Modal
    window.openSyllabusModal = (courseId) => {
        currentSyllabusCourseId = courseId;
        const data = syllabusData[courseId];
        if (!data) return;

        // Populate header details
        document.getElementById('modal-trust-pill').innerText = data.trustPill;
        
        // Populate title with status badge
        const titleElem = document.getElementById('modal-title');
        titleElem.innerHTML = `${data.title} <span class="status-badge ${data.status}" style="margin-left: 10px; font-size: 10px; padding: 0.2rem 0.6rem; border-radius: 4px; vertical-align: middle;">${data.statusText}</span>`;

        // Populate Quick Reference
        document.getElementById('modal-ref-exam').innerText = data.exam;
        document.getElementById('modal-ref-credential').innerText = data.credential;
        document.getElementById('modal-ref-level').innerText = data.level;
        document.getElementById('modal-ref-cost').innerText = data.cost;

        // Populate Exam weights list
        const weightList = document.getElementById('modal-weight-list');
        weightList.innerHTML = '';
        data.weights.forEach(w => {
            const li = document.createElement('li');
            li.style.display = 'flex';
            li.style.justifyContent = 'space-between';
            li.style.gap = '1rem';
            li.innerHTML = `<span style="flex: 1;">${w.topic}</span><span style="color: white; font-weight: 600; text-align: right; white-space: nowrap;">${w.weight}</span>`;
            weightList.appendChild(li);
        });

        // Populate Overview description
        const descContainer = document.getElementById('modal-overview-desc');
        descContainer.innerHTML = '';
        data.description.forEach(p => {
            const pElem = document.createElement('p');
            pElem.style.marginBottom = '1rem';
            pElem.innerHTML = p;
            descContainer.appendChild(pElem);
        });

        // Populate Tracks
        const tracksContainer = document.getElementById('modal-tracks-container');
        tracksContainer.innerHTML = '';
        data.tracks.forEach(track => {
            const div = document.createElement('div');
            div.className = 'track-block glass-panel';
            div.style.padding = '1.2rem';
            div.style.background = 'rgba(5, 7, 15, 0.3)';
            div.style.borderColor = 'rgba(255, 255, 255, 0.05)';
            div.innerHTML = `<h5 class="text-master-gold" style="font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;">${track.title}</h5>
                             <p style="font-size: 0.9rem; color: var(--text-muted); line-height: 1.5;">${track.desc}</p>`;
            tracksContainer.appendChild(div);
        });

        // Populate Labs
        const labsContainer = document.getElementById('modal-labs-container');
        labsContainer.innerHTML = '';
        data.labs.forEach(lab => {
            const div = document.createElement('div');
            div.className = 'lab-block glass-panel';
            div.style.padding = '1rem';
            div.style.borderColor = 'rgba(0, 240, 255, 0.15)';
            div.innerHTML = `<span class="lab-badge" style="background: rgba(0, 240, 255, 0.1); color: var(--accent-blue); padding: 0.2rem 0.5rem; font-size: 0.8rem; border-radius: 4px; font-family: var(--font-mono); font-weight: 700;">${lab.num}</span>
                             <h5 class="text-white" style="font-weight: 700; font-size: 0.95rem; margin-top: 0.4rem; margin-bottom: 0.2rem;">${lab.title}</h5>
                             <p style="font-size: 0.85rem; color: var(--text-muted);">${lab.desc}</p>`;
            labsContainer.appendChild(div);
        });

        // Default to Overview tab when opening
        switchSyllabusTab('overview');

        const modal = document.getElementById('syllabus-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    };

    window.closeSyllabusModal = () => {
        const modal = document.getElementById('syllabus-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    };

    window.beginSyllabusAscent = () => {
        closeSyllabusModal();
        openAssistant();
        if (currentSyllabusCourseId === 'dp900') {
            addMessage('user', "Begin DP-900 Ascent");
            callNIM("Let's begin the DP-900 Azure Data Fundamentals Ascent! Explain the core difference between relational and non-relational databases on Azure.");
        } else if (currentSyllabusCourseId === 'dp600') {
            addMessage('user', "Begin DP-600 Ascent");
            callNIM("Let's begin the DP-600 Microsoft Fabric Analytics Engineer Ascent! Tell me about Lab 01.");
        } else {
            addMessage('user', "Begin DP-700 Ascent");
            callNIM("Let's begin the DP-700 Microsoft Fabric Data Engineer Ascent! Tell me about Lab 01.");
        }
    };

    window.switchSyllabusTab = (tabId) => {
        // Deactivate all tab buttons
        const tabBtns = document.querySelectorAll('.modal-tab-btn');
        tabBtns.forEach(btn => btn.classList.remove('active'));

        // Activate the selected tab button
        const activeBtn = document.querySelector(`.modal-tab-btn[data-tab="${tabId}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        // Hide all tab panes
        const tabPanes = document.querySelectorAll('.modal-tab-pane');
        tabPanes.forEach(pane => pane.classList.remove('active'));

        // Show the selected tab pane
        const activePane = document.getElementById(`tab-${tabId}`);
        if (activePane) activePane.classList.add('active');
    };
});
