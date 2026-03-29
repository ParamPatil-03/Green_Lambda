
/* --- green_lambda_inject.js --- */
(function () {
    'use strict';
    let retries = 0;

    function injectGreenLambdaLoader() {
        // Evaluate Navigation State: Only play animation on First Load OR Explicit Reload
        const isReload = performance.getEntriesByType("navigation")?.[0]?.type === "reload";
        const hasSeenLoader = sessionStorage.getItem('greenlambda.hasSeenLoader');

        const loaderAnimation = document.querySelector('.ic-loader-animation');

        // If they have already seen the loader in this session and are NOT reloading, abort injection
        if (!isReload && hasSeenLoader) return;

        if (loaderAnimation) {
            console.log('Found loader animation container, injecting GREEN LAMBDA...');
            sessionStorage.setItem('greenlambda.hasSeenLoader', 'true');

            loaderAnimation.innerHTML = '';

            const svgHTML = `
<svg viewBox="0 0 1300 200" xmlns="http://www.w3.org/2000/svg" width="100%" height="auto" style="max-width: 90vw; margin: auto; display: block; transform: scale(1.8);">
  <rect width="1300" height="200" fill="#000000" class="svg-elem-1"></rect>
  <defs>
    <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#BFFF00;stop-opacity:1"></stop>
      <stop offset="50%" style="stop-color:#00FF00;stop-opacity:1"></stop>
      <stop offset="100%" style="stop-color:#00FFFF;stop-opacity:1"></stop>
    </linearGradient>
  </defs>
  <path d="M 50 150 Q 50 50 100 50 Q 150 50 150 100 L 150 150 Q 150 165 100 165 Q 85 165 85 150 L 85 95 L 130 95" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-2"></path>
  <path d="M 180 165 L 180 50 L 230 50 Q 255 50 255 75 Q 255 95 230 95 L 180 95 M 220 95 L 255 165" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-3"></path>
  <path d="M 285 165 L 285 50 L 345 50 M 285 107 L 335 107 M 285 165 L 345 165" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-4"></path>
  <path d="M 375 165 L 375 50 L 435 50 M 375 107 L 425 107 M 375 165 L 435 165" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-5"></path>
  <path d="M 465 165 L 465 50 L 535 165 L 535 50" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-6"></path>
  <path d="M 655 50 L 655 165 L 715 165" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-7"></path>
  <path d="M 745 165 L 780 50 L 815 165 M 760 110 L 800 110" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-8"></path>
  <path d="M 845 165 L 845 50 L 880 110 L 915 50 L 915 165" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-9"></path>
  <path d="M 945 165 L 945 50 L 995 50 Q 1020 50 1020 72 Q 1020 95 995 95 L 945 95 M 945 95 L 995 95 Q 1020 95 1020 130 Q 1020 165 995 165 L 945 165" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-10"></path>
  <path d="M 1050 165 L 1050 50 L 1100 50 Q 1140 50 1140 107 Q 1140 165 1100 165 L 1050 165" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-11"></path>
  <path d="M 1170 165 L 1205 50 L 1240 165 M 1185 110 L 1225 110" fill="none" stroke="url(#greenGradient)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" class="svg-elem-12"></path>
</svg>`;

            loaderAnimation.innerHTML = svgHTML;

            setTimeout(() => {
                const svg = loaderAnimation.querySelector('svg');
                if (svg) {
                    svg.classList.add('active');
                    console.log('GREEN LAMBDA animation triggered!');
                }
            }, 100);
        } else if (retries < 20) {
            retries++;
            setTimeout(injectGreenLambdaLoader, 50);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectGreenLambdaLoader);
    } else {
        injectGreenLambdaLoader();
    }
})();


/* --- vortex.js --- */
(function () {
    'use strict';

    const canvasId = 'vortexCanvas';
    let canvas, ctx;
    let tick = 0;
    let particleProps;
    let center = [0, 0];
    let simplex;

    const particleCount = 700;
    const particlePropCount = 9;
    const particlePropsLength = particleCount * particlePropCount;
    const rangeY = 100;
    const baseTTL = 50;
    const rangeTTL = 150;
    const baseSpeed = 0.0;
    const rangeSpeed = 1.5;
    const baseRadius = 1;
    const rangeRadius = 2;
    const baseHue = 70;
    const rangeHue = 110;
    const noiseSteps = 3;
    const xOff = 0.00125;
    const yOff = 0.00125;
    const zOff = 0.0005;
    const backgroundColor = 'transparent';

    const TAU = 2 * Math.PI;
    const rand = (n) => n * Math.random();
    const randRange = (n) => n - rand(2 * n);
    const fadeInOut = (t, m) => {
        let hm = 0.5 * m;
        return Math.abs(((t + hm) % m) - hm) / hm;
    };
    const lerp = (n1, n2, speed) => (1 - speed) * n1 + speed * n2;

    function initVortex() {
        canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id ${canvasId} not found`);
            return;
        }
        ctx = canvas.getContext('2d');

        if (typeof SimplexNoise === 'undefined') {
            console.error('SimplexNoise library not loaded.');
            return;
        }
        simplex = new SimplexNoise();

        resize();
        initParticles();
        draw();

        window.addEventListener('resize', resize);
    }

    function initParticles() {
        tick = 0;
        particleProps = new Float32Array(particlePropsLength);
        for (let i = 0; i < particlePropsLength; i += particlePropCount) {
            initParticle(i);
        }
    }

    function initParticle(i) {
        let x, y, vx, vy, life, ttl, speed, radius, hue;

        x = rand(canvas.width);
        y = center[1] + randRange(rangeY);
        vx = 0;
        vy = 0;
        life = 0;
        ttl = baseTTL + rand(rangeTTL);
        speed = baseSpeed + rand(rangeSpeed);
        radius = baseRadius + rand(rangeRadius);
        hue = baseHue + rand(rangeHue);

        particleProps.set([x, y, vx, vy, life, ttl, speed, radius, hue], i);
    }

    function draw() {
        tick++;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        drawParticles();

        renderGlow();

        window.requestAnimationFrame(draw);
    }

    function drawParticles() {
        for (let i = 0; i < particlePropsLength; i += particlePropCount) {
            updateParticle(i);
        }
    }

    function updateParticle(i) {
        let i2 = 1 + i, i3 = 2 + i, i4 = 3 + i, i5 = 4 + i,
            i6 = 5 + i, i7 = 6 + i, i8 = 7 + i, i9 = 8 + i;
        let n, x, y, vx, vy, life, ttl, speed, x2, y2, radius, hue;

        x = particleProps[i];
        y = particleProps[i2];

        n = simplex.noise3D(x * xOff, y * yOff, tick * zOff) * noiseSteps * TAU;

        vx = lerp(particleProps[i3], Math.cos(n), 0.5);
        vy = lerp(particleProps[i4], Math.sin(n), 0.5);
        life = particleProps[i5];
        ttl = particleProps[i6];
        speed = particleProps[i7];
        x2 = x + vx * speed;
        y2 = y + vy * speed;
        radius = particleProps[i8];
        hue = particleProps[i9];

        drawParticle(x, y, x2, y2, life, ttl, radius, hue);

        life++;
        particleProps[i] = x2;
        particleProps[i2] = y2;
        particleProps[i3] = vx;
        particleProps[i4] = vy;
        particleProps[i5] = life;

        if (checkBounds(x, y) || life > ttl) {
            initParticle(i);
        }
    }

    function drawParticle(x, y, x2, y2, life, ttl, radius, hue) {
        ctx.save();
        ctx.lineCap = 'round';
        ctx.lineWidth = radius;
        ctx.strokeStyle = `hsla(${hue},100%,60%,${fadeInOut(life, ttl)})`;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        ctx.closePath();
        ctx.restore();
    }

    function checkBounds(x, y) {
        return x > canvas.width || x < 0 || y > canvas.height || y < 0;
    }

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        center[0] = 0.5 * canvas.width;
        center[1] = 0.5 * canvas.height;
    }

    function renderGlow() {
        ctx.save();
        ctx.filter = 'blur(8px) brightness(200%)';
        ctx.globalCompositeOperation = 'lighter';
        ctx.drawImage(canvas, 0, 0);
        ctx.restore();

        ctx.save();
        ctx.filter = 'blur(4px) brightness(200%)';
        ctx.globalCompositeOperation = 'lighter';
        ctx.drawImage(canvas, 0, 0);
        ctx.restore();
    }

    window.addEventListener('load', initVortex);

})();


/* --- cursor.js --- */
(function () {
    'use strict';

    const config = {
        targetSelector: 'a, button, .btn, input, select, textarea, .cursor-target, .pillar-card, .fw-step, .kpi-card, .dash-card, .partner-card, .model-card, .chip, .result-card, .editor-container, .ms-btn, .bb8-toggle, .analyze-main label',
        spinDuration: 2,
        hideDefaultCursor: true,
        hoverDuration: 0.2,
        parallaxOn: true,
        borderWidth: 3,
        cornerSize: 12
    };

    let cursor, dot, corners;
    let spinTl;
    let isActive = false;
    let activeStrength = { current: 0 };
    let targetCornerPositions = null;
    let activeTarget = null;
    let currentLeaveHandler = null;
    let resumeTimeout = null;

    const isMobile = () => {
        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
        const mobileRegex = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i;
        return mobileRegex.test(userAgent.toLowerCase());
    };

    function initTargetCursor() {
        if (typeof gsap === 'undefined') {
            console.error('GSAP library not loaded.');
            return;
        }

        if (config.hideDefaultCursor) {
            document.body.style.cursor = 'none';
            const style = document.createElement('style');
            style.textContent = `* { cursor: none !important; }`;
            document.head.appendChild(style);
        }

        const wrapper = document.createElement('div');
        wrapper.className = 'target-cursor-wrapper';
        wrapper.innerHTML = `
            <div class="target-cursor-dot"></div>
            <div class="target-cursor-corner corner-tl"></div>
            <div class="target-cursor-corner corner-tr"></div>
            <div class="target-cursor-corner corner-br"></div>
            <div class="target-cursor-corner corner-bl"></div>
        `;
        document.body.appendChild(wrapper);

        cursor = wrapper;
        dot = wrapper.querySelector('.target-cursor-dot');
        corners = wrapper.querySelectorAll('.target-cursor-corner');

        gsap.set(cursor, {
            xPercent: -50,
            yPercent: -50,
            x: window.innerWidth / 2,
            y: window.innerHeight / 2
        });

        createSpinTimeline();

        window.addEventListener('mousemove', moveHandler, { capture: true });
        window.addEventListener('scroll', scrollHandler, { passive: true, capture: true });
        window.addEventListener('mousedown', mouseDownHandler, { capture: true });
        window.addEventListener('mouseup', mouseUpHandler, { capture: true });

        document.addEventListener('mouseover', enterHandler, { capture: true });
    }

    function createSpinTimeline() {
        if (spinTl) spinTl.kill();
        spinTl = gsap.timeline({ repeat: -1 })
            .to(cursor, { rotation: '+=360', duration: config.spinDuration, ease: 'none' });
    }

    function moveCursor(x, y) {
        if (!cursor) return;
        gsap.to(cursor, {
            x: x,
            y: y,
            duration: 0.1,
            ease: 'power3.out'
        });
    }

    const moveHandler = (e) => moveCursor(e.clientX, e.clientY);

    const scrollHandler = () => {
        if (!activeTarget || !cursor) return;
        const mouseX = gsap.getProperty(cursor, 'x');
        const mouseY = gsap.getProperty(cursor, 'y');
        const elementUnderMouse = document.elementFromPoint(mouseX, mouseY);

        const isStillOverTarget = elementUnderMouse &&
            (elementUnderMouse === activeTarget || elementUnderMouse.closest(config.targetSelector) === activeTarget);

        if (!isStillOverTarget && currentLeaveHandler) {
            currentLeaveHandler();
        }
    };

    const mouseDownHandler = () => {
        if (!dot) return;
        gsap.to(dot, { scale: 0.7, duration: 0.3 });
        gsap.to(cursor, { scale: 0.9, duration: 0.2 });
    };

    const mouseUpHandler = () => {
        if (!dot) return;
        gsap.to(dot, { scale: 1, duration: 0.3 });
        gsap.to(cursor, { scale: 1, duration: 0.2 });
    };

    const tickerFn = () => {
        if (!targetCornerPositions || !cursor || !corners) return;

        const strength = activeStrength.current;
        if (strength === 0) return;

        const cursorX = gsap.getProperty(cursor, 'x');
        const cursorY = gsap.getProperty(cursor, 'y');

        corners.forEach((corner, i) => {
            const currentX = gsap.getProperty(corner, 'x');
            const currentY = gsap.getProperty(corner, 'y');

            const targetX = targetCornerPositions[i].x - cursorX;
            const targetY = targetCornerPositions[i].y - cursorY;

            const finalX = currentX + (targetX - currentX) * strength;
            const finalY = currentY + (targetY - currentY) * strength;

            const duration = strength >= 0.99 ? (config.parallaxOn ? 0.2 : 0) : 0.05;

            gsap.to(corner, {
                x: finalX,
                y: finalY,
                duration: duration,
                ease: duration === 0 ? 'none' : 'power1.out',
                overwrite: 'auto'
            });
        });
    };

    const enterHandler = (e) => {
        const target = e.target.closest(config.targetSelector);

        if (!target || !cursor) return;
        if (activeTarget === target) return;

        if (activeTarget && currentLeaveHandler) {
            currentLeaveHandler();
        }

        if (resumeTimeout) {
            clearTimeout(resumeTimeout);
            resumeTimeout = null;
        }

        activeTarget = target;

        corners.forEach(corner => gsap.killTweensOf(corner));
        gsap.killTweensOf(cursor, 'rotation');
        if (spinTl) spinTl.pause();
        gsap.set(cursor, { rotation: 0 });

        const rect = target.getBoundingClientRect();
        const { borderWidth, cornerSize } = config;

        targetCornerPositions = [
            { x: rect.left - borderWidth, y: rect.top - borderWidth },
            { x: rect.right + borderWidth - cornerSize, y: rect.top - borderWidth },
            { x: rect.right + borderWidth - cornerSize, y: rect.bottom + borderWidth - cornerSize },
            { x: rect.left - borderWidth, y: rect.bottom + borderWidth - cornerSize }
        ];

        isActive = true;
        gsap.ticker.add(tickerFn);

        gsap.to(activeStrength, {
            current: 1,
            duration: config.hoverDuration,
            ease: 'power2.out'
        });

        const cursorX = gsap.getProperty(cursor, 'x');
        const cursorY = gsap.getProperty(cursor, 'y');

        corners.forEach((corner, i) => {
            gsap.to(corner, {
                x: targetCornerPositions[i].x - cursorX,
                y: targetCornerPositions[i].y - cursorY,
                duration: 0.2,
                ease: 'power2.out'
            });
        });

        const leaveHandler = () => {
            target.removeEventListener('mouseleave', leaveHandler);
            currentLeaveHandler = null;

            gsap.ticker.remove(tickerFn);

            isActive = false;
            targetCornerPositions = null;
            gsap.set(activeStrength, { current: 0, overwrite: true });
            activeTarget = null;

            gsap.killTweensOf(corners);
            const { cornerSize } = config;

            const positions = [
                { x: 0, y: 0 },
                { x: 0, y: 0 },
                { x: 0, y: 0 },
                { x: 0, y: 0 }
            ];

            resumeTimeout = setTimeout(() => {
                if (!activeTarget && cursor && spinTl) {
                    const currentRotation = gsap.getProperty(cursor, 'rotation');
                    const normalized = currentRotation % 360;
                    spinTl.kill();
                    spinTl = gsap.timeline({ repeat: -1 })
                        .to(cursor, { rotation: '+=360', duration: config.spinDuration, ease: 'none' });

                    gsap.to(cursor, {
                        rotation: normalized + 360,
                        duration: config.spinDuration * (1 - normalized / 360),
                        ease: 'none',
                        onComplete: () => spinTl.restart()
                    });
                }
                resumeTimeout = null;
            }, 50);

            corners.forEach(corner => {
                gsap.to(corner, {
                    x: 0,
                    y: 0,
                    duration: 0.3,
                    ease: 'power3.out',
                    clearProps: 'x,y'
                });
            });
        };

        currentLeaveHandler = leaveHandler;
        target.addEventListener('mouseleave', leaveHandler);
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTargetCursor);
    } else {
        initTargetCursor();
    }

})();


/* --- rotating-text.js --- */
(function () {
    'use strict';

    const config = {
        selector: '#rotatingText',
        texts: ['Design', 'Develop', 'Deploy'],
        rotationInterval: 2000,
        transition: {
            duration: 0.5,
            ease: "back.out(1.7)"
        }
    };

    let container;
    let currentTextIndex = 0;
    let isAnimating = false;

    function initRotatingText() {
        container = document.querySelector(config.selector);
        if (!container) return;

        if (typeof gsap === 'undefined') {
            console.error('GSAP not loaded for Rotating Text');
            return;
        }

        renderText(config.texts[0]);

        setTimeout(next, config.rotationInterval);
    }

    function renderText(text) {
        container.innerHTML = '';

        const srText = document.createElement('span');
        srText.className = 'text-rotate-sr-only';
        srText.textContent = text;
        container.appendChild(srText);

        const visibleWrapper = document.createElement('span');
        visibleWrapper.className = 'text-rotate-word';
        visibleWrapper.textContent = text;
        visibleWrapper.style.display = 'inline-block';
        visibleWrapper.style.opacity = '1';
        visibleWrapper.style.transform = 'translateY(0)';

        container.appendChild(visibleWrapper);
    }

    function next() {
        if (isAnimating) return;
        isAnimating = true;

        const currentWord = container.querySelector('.text-rotate-word');

        gsap.to(currentWord, {
            y: '-120%',
            opacity: 0,
            duration: config.transition.duration,
            ease: "power2.in",
            onComplete: () => {
                currentTextIndex = (currentTextIndex + 1) % config.texts.length;
                const nextText = config.texts[currentTextIndex];

                renderText(nextText);

                const newWord = container.querySelector('.text-rotate-word');

                gsap.set(newWord, { y: '100%', opacity: 0 });

                gsap.to(newWord, {
                    y: '0%',
                    opacity: 1,
                    duration: config.transition.duration,
                    ease: config.transition.ease,
                    onComplete: () => {
                        isAnimating = false;
                        setTimeout(next, config.rotationInterval);
                    }
                });
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRotatingText);
    } else {
        initRotatingText();
    }

})();


/* --- cyber_card.js --- */
document.addEventListener('DOMContentLoaded', () => {
    // Select the cards to apply the effect to
    const targets = document.querySelectorAll('.pillar-card, .model-card, .partner-card, .kpi-card, .fw-step');

    targets.forEach((card) => {
        // Prepare original content nodes
        const originalChildren = Array.from(card.childNodes);

        // Turn the card itself into the cyber-container
        card.classList.add('cyber-container');

        // Create canvas
        const canvas = document.createElement('div');
        canvas.className = 'cyber-canvas';

        // Add 25 trackers
        for (let i = 1; i <= 25; i++) {
            const tracker = document.createElement('div');
            tracker.className = `cyber-tracker tr-${i}`;
            canvas.appendChild(tracker);
        }

        const cyberCardInner = document.createElement('div');
        cyberCardInner.className = 'cyber-card-inner';

        const cyberContent = document.createElement('div');
        cyberContent.className = 'cyber-content';

        const cyberGlare = document.createElement('div');
        cyberGlare.className = 'cyber-glare';

        const cyberLines = document.createElement('div');
        cyberLines.className = 'cyber-lines';
        cyberLines.innerHTML = '<span></span><span></span><span></span><span></span>';

        const cyberGlowingElements = document.createElement('div');
        cyberGlowingElements.className = 'cyber-glowing-elements';
        cyberGlowingElements.innerHTML = '<div class="glow-1"></div><div class="glow-2"></div><div class="glow-3"></div>';

        const cyberParticles = document.createElement('div');
        cyberParticles.className = 'cyber-particles';
        cyberParticles.innerHTML = '<span></span><span></span><span></span><span></span><span></span><span></span>';

        const cyberCornerElements = document.createElement('div');
        cyberCornerElements.className = 'cyber-corner-elements';
        cyberCornerElements.innerHTML = '<span></span><span></span><span></span><span></span>';

        const cyberScanLine = document.createElement('div');
        cyberScanLine.className = 'cyber-scan-line';

        const originalContentWrapper = document.createElement('div');
        originalContentWrapper.className = 'cyber-original-content';

        // Assemble hierarchy
        cyberContent.appendChild(cyberGlare);
        cyberContent.appendChild(cyberLines);

        // Put original children securely into wrapper Without breaking DOM refs!
        originalChildren.forEach(child => {
            originalContentWrapper.appendChild(child);
        });
        cyberContent.appendChild(originalContentWrapper);

        cyberContent.appendChild(cyberGlowingElements);
        cyberContent.appendChild(cyberParticles);
        cyberContent.appendChild(cyberCornerElements);
        cyberContent.appendChild(cyberScanLine);

        cyberCardInner.appendChild(cyberContent);
        canvas.appendChild(cyberCardInner);

        card.appendChild(canvas);

        // Remove old visual styles that were on the outer card wrapper natively
        card.style.background = 'transparent';
        card.style.borderColor = 'transparent';
        card.style.boxShadow = 'none';
        card.style.padding = '0';
    });
});

/* --- original script.js --- */
const initApp = async () => {
    const page = document.body?.dataset?.page || 'home';
    console.log(`Green Lambda App Initializing (${page})...`);

    // ── Hydrate local cache from Supabase ──
    if (page !== 'login') {
        await checkAuth();
    }

    initScrollReveal();
    initNavigation();
    initScrollProgress();

    if (page === 'home') {
        initHeroCanvas();
        initKPICounters();
        initLiveMetrics();
        initCharts();
        populateTable();
        initSearch();
        initChipButtons();
        initDiscoverModal();
    }

    if (page === 'connect') {
        initConnectPage();
    }

    if (page === 'analyze') {
        initAnalyzePage();
    }

    if (page === 'dashboard') {
        initDashboardPage();
    }
    if (page === 'login') {
        initLoginPage();
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px'
    });

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

function initNavigation() {
    const nav = document.getElementById('nav');
    const links = document.querySelectorAll('.nav-link');
    const toggle = document.getElementById('navToggle');
    const navLinksWrap = document.getElementById('navLinks');

    const sections = document.querySelectorAll('.section');
    const sectionMap = {};
    sections.forEach(s => { if (s.id) sectionMap[s.id] = s; });

    window.addEventListener('scroll', () => {
        nav.classList.toggle('scrolled', window.scrollY > 50);

        const page = document.body?.dataset?.page || 'home';
        if (page !== 'home') return; // Don't do scrollSpy on subpages, keeps active state intact

        let current = '';
        sections.forEach(s => {
            const top = s.offsetTop - 100;
            if (window.scrollY >= top) current = s.id;
        });

        links.forEach(l => {
            if (!l.dataset.section) return;
            l.classList.toggle('active', l.dataset.section === current);
        });
    });

    links.forEach(link => {
        link.addEventListener('click', e => {
            const sectionId = link.dataset.section;
            if (!sectionId) return; // Allow normal navigation if no data-section exists

            const target = document.getElementById(sectionId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
                if (navLinksWrap) navLinksWrap.classList.remove('open');
            }
        });
    });

    if (toggle) {
        toggle.addEventListener('click', () => {
            navLinksWrap.classList.toggle('open');
        });
    }
}

function initScrollProgress() {
    const bar = document.getElementById('scrollProgress');
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const max = document.documentElement.scrollHeight - window.innerHeight;
        const pct = Math.min((scrolled / max) * 100, 100);
        bar.style.width = pct + '%';
    });
}

function initHeroCanvas() {
    const canvas = document.getElementById('heroCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let w, h;

    function resize() {
        const rect = canvas.parentElement.getBoundingClientRect();
        w = canvas.width = rect.width;
        h = canvas.height = rect.height;
    }
    resize();
    window.addEventListener('resize', resize);

    class Dot {
        constructor() {
            this.x = Math.random() * w;
            this.y = Math.random() * h;
            this.vx = (Math.random() - 0.5) * 0.25;
            this.vy = (Math.random() - 0.5) * 0.25;
            this.r = Math.random() * 1.5 + 0.3;
            this.alpha = Math.random() * 0.25 + 0.05;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > w) this.vx *= -1;
            if (this.y < 0 || this.y > h) this.vy *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(200, 255, 0, ${this.alpha})`;
            ctx.fill();
        }
    }

    const count = Math.min(60, Math.floor(w * h / 20000));
    for (let i = 0; i < count; i++) particles.push(new Dot());

    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 160) {
                    const alpha = (1 - dist / 160) * 0.04;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(200, 255, 0, ${alpha})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }

    function loop() {
        ctx.clearRect(0, 0, w, h);
        particles.forEach(p => { p.update(); p.draw(); });
        drawConnections();
        requestAnimationFrame(loop);
    }
    loop();
}

function initKPICounters() {
    const targets = [
        { id: 'kpiEnergy', end: 0.85, dec: 2 },
        { id: 'kpiCost', end: 320, dec: 0 },
        { id: 'kpiCarbon', end: 0.6, dec: 1 },
        { id: 'kpiAccuracy', end: 0.9999, dec: 4 }
    ];

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                targets.forEach(t => {
                    const el = document.getElementById(t.id);
                    if (el && !el.dataset.counted) {
                        el.dataset.counted = '1';
                        animateCounter(el, 0, t.end, 2000, t.dec);
                    }
                });
                observer.disconnect();
            }
        });
    }, { threshold: 0.3 });

    const kpiRow = document.querySelector('.kpi-row');
    if (kpiRow) observer.observe(kpiRow);
}

function animateCounter(el, start, end, dur, dec) {
    const t0 = performance.now();
    function tick(now) {
        const p = Math.min((now - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = (start + (end - start) * eased).toFixed(dec);
        if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

function initLiveMetrics() {
    const bars = document.querySelectorAll('.metric-fill[data-base]');

    function update() {
        bars.forEach(bar => {
            const base = parseFloat(bar.dataset.base);
            const variance = parseFloat(bar.dataset.var);
            const val = Math.max(5, Math.min(95, base + (Math.random() - 0.5) * variance));
            bar.style.width = val + '%';

            const row = bar.closest('.metric-row');
            const valEl = row ? row.querySelector('.metric-val') : null;
            if (valEl) valEl.textContent = Math.round(val) + '%';
        });
    }

    setTimeout(update, 500);
    setInterval(update, 2500);
}

function initCharts() {
    if (typeof Chart === 'undefined') return;
    Chart.defaults.color = '#555555';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;

    const tooltipStyle = {
        backgroundColor: 'rgba(10,10,10,0.92)',
        borderColor: 'rgba(200,255,0,0.15)',
        borderWidth: 1,
        titleFont: { family: "'JetBrains Mono', monospace", size: 11 },
        bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
        padding: 10,
        cornerRadius: 8
    };

    const energyCtx = document.getElementById('energyChart');
    if (energyCtx) {
        new Chart(energyCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [
                    {
                        label: 'Predicted',
                        data: [0.32, 0.38, 0.41, 0.35, 0.46, 0.29, 0.34],
                        borderColor: '#c8ff00',
                        backgroundColor: 'rgba(200,255,0,0.04)',
                        borderWidth: 2, fill: true, tension: 0.4,
                        pointRadius: 3, pointBackgroundColor: '#c8ff00', pointBorderWidth: 0, pointHoverRadius: 6
                    },
                    {
                        label: 'Actual',
                        data: [0.31, 0.39, 0.38, 0.37, 0.43, 0.31, 0.35],
                        borderColor: '#7b61ff',
                        backgroundColor: 'rgba(123,97,255,0.03)',
                        borderWidth: 2, fill: true, tension: 0.4,
                        pointRadius: 3, pointBackgroundColor: '#7b61ff', pointBorderWidth: 0, pointHoverRadius: 6
                    },
                    {
                        label: 'Optimized',
                        data: [0.24, 0.28, 0.30, 0.26, 0.34, 0.21, 0.25],
                        borderColor: '#36f9ae',
                        backgroundColor: 'rgba(54,249,174,0.02)',
                        borderWidth: 2, borderDash: [5, 5], fill: true, tension: 0.4,
                        pointRadius: 2, pointBackgroundColor: '#36f9ae', pointBorderWidth: 0
                    }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                hover: { mode: 'nearest', intersect: true },
                events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'],
                plugins: {
                    legend: { position: 'top', align: 'end', labels: { boxWidth: 12, boxHeight: 2, padding: 16 } },
                    tooltip: { ...tooltipStyle, callbacks: { label: c => ` ${c.dataset.label}: ${c.raw} kWh` } }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { callback: v => v + ' kWh' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    const distCtx = document.getElementById('distChart');
    if (distCtx) {
        new Chart(distCtx, {
            type: 'doughnut',
            data: {
                labels: ['Memory Allocation', 'Compute Cycles', 'Network I/O', 'Cold Starts', 'Garbage Collection', 'Init Overhead'],
                datasets: [{
                    data: [35, 28, 18, 10, 6, 3],
                    backgroundColor: [
                        'rgba(200,255,0,0.65)', 'rgba(123,97,255,0.65)', 'rgba(54,249,174,0.65)',
                        'rgba(255,194,51,0.65)', 'rgba(255,61,113,0.65)', 'rgba(255,138,71,0.65)'
                    ],
                    borderWidth: 0, hoverOffset: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '65%',
                plugins: {
                    legend: { position: 'right', labels: { boxWidth: 8, boxHeight: 8, usePointStyle: true, pointStyle: 'circle', padding: 10, font: { size: 10 } } },
                    tooltip: { ...tooltipStyle, callbacks: { label: c => ` ${c.label}: ${c.raw}%` } }
                }
            }
        });
    }

    const featureCtx = document.getElementById('featureChart');
    if (featureCtx) {
        new Chart(featureCtx, {
            type: 'bar',
            data: {
                labels: ['Memory Func Type', 'Local Memory (MB)', 'Lines of Code', 'AWS Mem Used', 'Nesting Depth', 'Conditionals', 'Function Calls', 'Loop Count'],
                datasets: [{
                    label: 'SHAP Impact',
                    data: [0.687, 0.108, 0.033, 0.025, 0.015, 0.012, 0.007, 0.002],
                    backgroundColor: [
                        'rgba(200,255,0,0.5)', 'rgba(200,255,0,0.42)',
                        'rgba(123,97,255,0.5)', 'rgba(123,97,255,0.42)',
                        'rgba(54,249,174,0.5)', 'rgba(54,249,174,0.42)',
                        'rgba(255,194,51,0.5)', 'rgba(255,194,51,0.42)'
                    ],
                    borderColor: 'transparent', borderRadius: 4, borderSkipped: false, barThickness: 20
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: { ...tooltipStyle, callbacks: { label: c => ` Impact: ${c.raw.toFixed(2)}` } }
                },
                scales: {
                    x: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { callback: v => v.toFixed(1) } },
                    y: { grid: { display: false }, ticks: { font: { size: 10, family: "'JetBrains Mono', monospace" } } }
                }
            }
        });
    }

    const scatterCtx = document.getElementById('scatterChart');
    if (scatterCtx) {
        const data = [{ "x": 4.989, "y": 4.989 }, { "x": 4.345, "y": 4.344 }, { "x": 4.989, "y": 4.989 }, { "x": 1.906, "y": 1.906 }, { "x": 1.635, "y": 1.635 }, { "x": 2.832, "y": 2.832 }, { "x": 1.441, "y": 1.441 }, { "x": 1.739, "y": 1.740 }, { "x": 3.818, "y": 3.818 }, { "x": 3.109, "y": 3.109 }, { "x": 2.070, "y": 2.070 }, { "x": 1.739, "y": 1.739 }, { "x": 5.159, "y": 5.163 }, { "x": 4.095, "y": 4.095 }, { "x": 4.013, "y": 4.013 }, { "x": 3.818, "y": 3.819 }, { "x": 1.441, "y": 1.441 }, { "x": 0.356, "y": 0.356 }, { "x": 2.464, "y": 2.464 }, { "x": 0.356, "y": 0.356 }, { "x": 4.585, "y": 4.585 }, { "x": 3.818, "y": 3.818 }, { "x": 4.826, "y": 4.826 }, { "x": 2.231, "y": 2.231 }, { "x": 5.074, "y": 5.063 }, { "x": 0.771, "y": 0.771 }, { "x": 3.352, "y": 3.352 }, { "x": 2.231, "y": 2.231 }, { "x": 1.988, "y": 1.988 }, { "x": 3.565, "y": 3.565 }, { "x": 2.708, "y": 2.708 }, { "x": 4.013, "y": 4.013 }, { "x": 2.708, "y": 2.708 }, { "x": 1.635, "y": 1.635 }, { "x": 2.593, "y": 2.591 }, { "x": 5.159, "y": 5.159 }, { "x": 0.056, "y": 0.056 }, { "x": 4.585, "y": 4.585 }, { "x": 4.095, "y": 4.095 }, { "x": 4.423, "y": 4.423 }, { "x": 0.356, "y": 0.356 }, { "x": 3.818, "y": 3.818 }, { "x": 1.821, "y": 1.821 }, { "x": 3.191, "y": 3.190 }, { "x": 4.181, "y": 4.180 }, { "x": 2.593, "y": 2.593 }, { "x": 4.505, "y": 4.505 }, { "x": 2.464, "y": 2.464 }, { "x": 0.056, "y": 0.056 }, { "x": 4.505, "y": 4.505 }, { "x": 1.739, "y": 1.739 }, { "x": 4.989, "y": 4.989 }, { "x": 4.013, "y": 4.013 }, { "x": 2.593, "y": 2.593 }, { "x": 4.345, "y": 4.345 }, { "x": 1.441, "y": 1.441 }, { "x": 2.593, "y": 2.593 }, { "x": 4.585, "y": 4.585 }, { "x": 2.149, "y": 2.149 }, { "x": 3.109, "y": 3.109 }];
        new Chart(scatterCtx, {
            type: 'scatter',
            data: {
                datasets: [
                    { label: 'Predictions', data, backgroundColor: 'rgba(200,255,0,0.45)', borderColor: 'rgba(200,255,0,0.7)', borderWidth: 1, pointRadius: 4, pointHoverRadius: 7 },
                    { label: 'Perfect', data: [{ x: 0, y: 0 }, { x: 6, y: 6 }], type: 'line', borderColor: 'rgba(255,255,255,0.12)', borderDash: [4, 4], borderWidth: 1.5, pointRadius: 0, fill: false }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', align: 'end', labels: { boxWidth: 10, boxHeight: 2, padding: 14 } },
                    tooltip: { ...tooltipStyle, callbacks: { label: c => ` Actual: ${c.raw.x.toFixed(2)} | Pred: ${c.raw.y.toFixed(2)} Wh` } }
                },
                scales: {
                    x: { title: { display: true, text: 'Actual (Wh)', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.03)' } },
                    y: { title: { display: true, text: 'Predicted (Wh)', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.03)' } }
                }
            }
        });
    }

    const radarCtx = document.getElementById('radarChart');
    if (radarCtx) {
        new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['R² Score', 'MAE', 'RMSE', 'Train Speed', 'Inference', 'Interpretability'],
                datasets: [
                    { label: 'XGBoost', data: [99.99, 98, 96, 92, 95, 82], borderColor: '#c8ff00', backgroundColor: 'rgba(200,255,0,0.06)', borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#c8ff00' },
                    { label: 'Random Forest', data: [99.99, 96, 98, 98, 90, 88], borderColor: '#36f9ae', backgroundColor: 'rgba(54,249,174,0.04)', borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#36f9ae' },
                    { label: 'Neural Net', data: [99.73, 85, 85, 96, 72, 40], borderColor: '#7b61ff', backgroundColor: 'rgba(123,97,255,0.04)', borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#7b61ff' }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'top', labels: { boxWidth: 10, boxHeight: 2, padding: 14, font: { size: 11 } } } },
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255,255,255,0.05)' },
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        pointLabels: { font: { size: 10, family: "'JetBrains Mono', monospace" }, color: '#8a8a8a' },
                        ticks: { display: false }, suggestedMin: 0, suggestedMax: 100, beginAtZero: true
                    }
                }
            }
        });
    }
}

const FUNCTIONS = [
    { name: 'bubble-sort', runtime: 'Python 3.11', cx: 4, energy: 0.128, inv: '12.4K', eff: 45, st: 'critical' },
    { name: 'fibonacci', runtime: 'Go 1.21', cx: 2, energy: 0.027, inv: '48.7K', eff: 94, st: 'optimal' },
    { name: 'matrix-multiply', runtime: 'Java 21', cx: 3, energy: 0.029, inv: '8.1K', eff: 65, st: 'warning' },
    { name: 'prime-calculator', runtime: 'Python 3.11', cx: 5, energy: 0.007, inv: '67.2K', eff: 97, st: 'optimal' },
    { name: 'simple-encryption', runtime: 'Node.js 20', cx: 3, energy: 0.001, inv: '1.8K', eff: 32, st: 'critical' },
    { name: 'api-fetcher', runtime: 'Node.js 20', cx: 2, energy: 0.106, inv: '23.4K', eff: 82, st: 'optimal' },
    { name: 'csv-processor', runtime: 'Python 3.11', cx: 4, energy: 0.006, inv: '5.6K', eff: 67, st: 'warning' },
    { name: 'file-reader', runtime: 'Go 1.21', cx: 4, energy: 0.014, inv: '9.3K', eff: 88, st: 'optimal' },
];

function populateTable() {
    const tbody = document.getElementById('fnTableBody');
    if (!tbody) return;

    FUNCTIONS.forEach(fn => {
        const color = fn.eff >= 80 ? '#36f9ae' : fn.eff >= 60 ? '#ffc233' : '#ff3d71';
        const eColor = fn.energy > 0.5 ? '#ff3d71' : fn.energy > 0.2 ? '#ffc233' : '#36f9ae';
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="fn-name">${fn.name}</span></td>
            <td>${fn.runtime}</td>
            <td>${fn.cx}</td>
            <td style="font-family:'JetBrains Mono',monospace;font-weight:600;color:${eColor}">${fn.energy.toFixed(2)}</td>
            <td>${fn.inv}</td>
            <td>
                <span class="eff-bar"><span class="eff-fill" style="width:${fn.eff}%;background:${color}"></span></span>
                ${fn.eff}%
            </td>
            <td><span class="badge ${fn.st}">${fn.st}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function initSearch() {
    const input = document.getElementById('fnSearch');
    if (!input) return;
    input.addEventListener('input', () => {
        const q = input.value.toLowerCase();
        document.querySelectorAll('#fnTableBody tr').forEach(row => {
            const name = row.querySelector('.fn-name')?.textContent.toLowerCase() || '';
            row.style.display = name.includes(q) ? '' : 'none';
        });
    });
}

function initChipButtons() {
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            chip.parentElement.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
        });
    });
}

function initDiscoverModal() {
    const modal = document.getElementById('discoverModal');
    const closeBtn = document.getElementById('discoverClose');
    const titleEl = document.getElementById('discoverTitle');
    const descEl = document.getElementById('discoverDesc');
    const discoverBtns = document.querySelectorAll('.discover-btn');

    if (!modal || !closeBtn) return;

    function openModal(title, content) {
        titleEl.textContent = title;
        descEl.innerHTML = content;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    discoverBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            // Prevent duplicate firing if inside a pillar-card
            e.stopPropagation();
            const title = btn.getAttribute('data-title');
            const content = btn.getAttribute('data-content');
            openModal(title, content);
        });
    });

    // The 3D Cyber Cards intercept mouse events via their tracking grids, 
    // so we make the entire card clickable to trigger its respective modal!
    const pillarCards = document.querySelectorAll('.pillar-card');
    pillarCards.forEach(card => {
        card.style.cursor = 'pointer'; // Make it obvious it's clickable
        card.addEventListener('click', (e) => {
            const btn = card.querySelector('.discover-btn');
            if (btn) {
                e.preventDefault();
                openModal(btn.getAttribute('data-title'), btn.getAttribute('data-content'));
            }
        });
    });

    closeBtn.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
}
/* workflow pages script */
const GREENLAMBDA_KEYS = {
    session: 'greenlambda.session',
    analysis: 'greenlambda.analysis',
    forecast: 'greenlambda.forecast',
    apiBase: 'greenlambda.apiBase'
};

function getStoredJson(key) {
    try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function setStoredJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function getSession() {
    return getStoredJson(GREENLAMBDA_KEYS.session);
}

function setSession(session) {
    setStoredJson(GREENLAMBDA_KEYS.session, session);
}

function getApiBase() {
    return window.GREENLAMBDA_API_BASE || localStorage.getItem(GREENLAMBDA_KEYS.apiBase) || 'http://127.0.0.1:5000';
}

function toQuery(params) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
            query.append(key, String(value));
        }
    });
    return query.toString();
}

async function apiRequest(path, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);

    const method = options.method || 'GET';
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    const req = {
        method,
        headers,
        signal: controller.signal
    };

    if (options.body !== undefined) {
        req.body = JSON.stringify(options.body);
    }

    try {
        const response = await fetch(`${getApiBase()}${path}`, req);
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(payload.message || `Request failed (${response.status})`);
        }
        return payload;
    } finally {
        clearTimeout(timeout);
    }
}

function setBanner(el, type, message) {
    if (!el) return;
    el.className = `status-banner show ${type}`;
    el.textContent = message;
}

function formatNumber(value) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return '--';
    return new Intl.NumberFormat('en-IN').format(numeric);
}

function formatCurrencyInr(value) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return '₹--';
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2
    }).format(numeric);
}

function normalizeFunctions(list) {
    if (!Array.isArray(list)) return [];

    return list
        .map((item) => {
            if (typeof item === 'string') {
                return { name: item, runtime: 'unknown', memoryMb: '--' };
            }

            return {
                name: item.name || item.functionName || item.function_name || 'unknown-function',
                runtime: item.runtime || item.Runtime || 'unknown',
                memoryMb: item.memoryMb || item.memory_size || item.memorySize || item.MemorySize || '--'
            };
        })
        .filter((item) => item.name && item.name !== 'unknown-function');
}

function createDemoConnection(region) {
    // Functions match actual dataset names used in ML training
    return {
        connectionId: `demo-${Date.now()}`,
        functions: [
            { name: 'bubble-sort', runtime: 'python3.11', memoryMb: 256 },
            { name: 'fibonacci', runtime: 'python3.11', memoryMb: 512 },
            { name: 'matrix-multiply', runtime: 'python3.11', memoryMb: 1024 },
            { name: 'prime-calculator', runtime: 'python3.11', memoryMb: 256 },
            { name: 'simple-encryption', runtime: 'nodejs20.x', memoryMb: 128 },
            { name: 'api-fetcher', runtime: 'nodejs20.x', memoryMb: 512 },
            { name: 'csv-processor', runtime: 'python3.11', memoryMb: 256 },
            { name: 'file-reader', runtime: 'python3.11', memoryMb: 512 },
            { name: 'json-parser', runtime: 'nodejs20.x', memoryMb: 256 },
            { name: 'image-resizer', runtime: 'python3.11', memoryMb: 1024 }
        ],
        region
    };
}

function createDemoAnalysis({ baselineRph, functionName, model }) {
    // Energy values derived from actual energy_target_wh in ML dataset
    // (averaged across Small/Medium/Large input sizes per function)
    // memoryMb and avgDurationMs used for AWS Lambda cost calculation
    const fnProfiles = {
        'bubble-sort': { energyWh: 0.394, confidence: 0.943, memoryMb: 256, avgDurationMs: 2890 },
        'fibonacci': { energyWh: 1.081, confidence: 0.951, memoryMb: 512, avgDurationMs: 1860 },
        'matrix-multiply': { energyWh: 1.533, confidence: 0.928, memoryMb: 1024, avgDurationMs: 520 },
        'prime-calculator': { energyWh: 1.822, confidence: 0.962, memoryMb: 256, avgDurationMs: 380 },
        'simple-encryption': { energyWh: 2.069, confidence: 0.937, memoryMb: 128, avgDurationMs: 62 },
        'api-fetcher': { energyWh: 2.337, confidence: 0.914, memoryMb: 512, avgDurationMs: 410 },
        'csv-processor': { energyWh: 2.711, confidence: 0.906, memoryMb: 256, avgDurationMs: 185 },
        'file-reader': { energyWh: 3.024, confidence: 0.921, memoryMb: 512, avgDurationMs: 210 },
        'json-parser': { energyWh: 3.271, confidence: 0.898, memoryMb: 256, avgDurationMs: 108 },
        'image-resizer': { energyWh: 1.640, confidence: 0.932, memoryMb: 1024, avgDurationMs: 740 }
    };

    const profile = fnProfiles[functionName] || { energyWh: 1.5, confidence: 0.93, memoryMb: 512, avgDurationMs: 500 };

    // Create deterministic variations per model so clicking a different model genuinely changes the prediction!
    let energyMod = 1.0;
    let confMod = 1.0;

    if (model === 'rf') {
        energyMod = 1.002;  // RF predicts slightly higher variance
        confMod = 0.985;    // RF confidence is slightly lower than XGBoost
    } else if (model === 'nn') {
        energyMod = 0.996;  // NN predicts slightly aggressively lower
        confMod = 0.965;    // NN confidence drops a bit due to sample size
    } else {
        // 'xgboost' is the baseline perfect model
        energyMod = 1.0;
        confMod = 1.0;
    }

    const energyWhPerInvocation = profile.energyWh * energyMod;
    const confidence = profile.confidence * confMod;

    const monthlyInvocations = Number(baselineRph || 10000) * 24 * 30;
    const monthlyEnergyKwh = (monthlyInvocations * energyWhPerInvocation) / 1000;

    // India grid emission factor: 0.708 kg CO₂ per kWh (CEA 2023)
    const monthlyCarbonKg = monthlyEnergyKwh * 0.708;

    // AWS Lambda pricing (ap-south-1 Mumbai region)
    // Compute: $0.0000166667 per GB-second → ₹0.001392 per GB-second (at ₹83.5/USD)
    // Request: $0.20 per 1M requests → ₹16.70 per 1M requests
    const gbSeconds = (profile.memoryMb / 1024) * (profile.avgDurationMs / 1000);
    const computeCostPerInvocation = gbSeconds * 0.001392;  // ₹ per invocation
    const requestCostPerInvocation = 16.70 / 1_000_000;     // ₹ per invocation
    const monthlyCostInr = monthlyInvocations * (computeCostPerInvocation + requestCostPerInvocation);

    return {
        energyWhPerInvocation,
        confidence,
        monthlyInvocations,
        monthlyCarbonKg,
        monthlyCostInr
    };
}

function createDemoSpike({ baselineRph, multiplier, durationHours }, analysis) {
    const baseReq = Number(baselineRph || 10000);
    const mul = Number(multiplier || 20);
    const duration = Number(durationHours || 72);
    const peakReqPerHour = baseReq * mul;
    const energyWhPerInvocation = Number(analysis.energyWhPerInvocation || 1.5);
    const totalInvocations = peakReqPerHour * duration;
    const totalEnergyKwh = (totalInvocations * energyWhPerInvocation) / 1000;

    // India grid emission factor: 0.708 kg CO₂ per kWh
    const totalCarbonKg = totalEnergyKwh * 0.708;

    // Estimate cost using analysis monthlyCostInr ratio scaled to spike volume
    const costPerInvocation = analysis.monthlyCostInr
        ? analysis.monthlyCostInr / analysis.monthlyInvocations
        : 0.0015; // fallback ₹ per invocation
    const totalCostInr = totalInvocations * costPerInvocation;

    const hourly = [];
    for (let hour = 1; hour <= duration; hour += 1) {
        // Simulate realistic traffic: ramp up, plateau, slight decay
        const progress = hour / duration;
        let shapeFactor;
        if (progress < 0.1) shapeFactor = 0.6 + (progress / 0.1) * 0.4;   // ramp up
        else if (progress < 0.85) shapeFactor = 1.0;                              // plateau
        else shapeFactor = 1.0 - (progress - 0.85) * 1.5;   // decay

        const jitter = 0.94 + Math.random() * 0.12;  // ±6% realistic jitter
        const req = Math.round(peakReqPerHour * shapeFactor * jitter);
        const energyKwh = (req * energyWhPerInvocation) / 1000;
        hourly.push({
            hour,
            predictedReqPerHour: req,
            predictedEnergyKwh: Number(energyKwh.toFixed(4))
        });
    }

    return {
        totals: {
            energyKwh: Number(totalEnergyKwh.toFixed(3)),
            carbonKg: Number(totalCarbonKg.toFixed(3)),
            costInr: Number(totalCostInr.toFixed(2)),
            peakReqPerHour
        },
        hourly
    };
}

function createDemoLiveMetrics(predictedReqPerHour) {
    const predicted = Number(predictedReqPerHour || 200000);
    // Realistic drift: most samples within ±6%, occasional outliers up to ±12%
    const isOutlier = Math.random() < 0.15;
    const driftRange = isOutlier ? 0.12 : 0.06;
    const drift = 1 + (Math.random() * 2 - 1) * driftRange;
    const actual = Math.round(predicted * drift);
    const deviationPct = ((actual - predicted) / predicted) * 100;

    return {
        predictedReqPerHour: predicted,
        actualReqPerHour: actual,
        deviationPct: Number(deviationPct.toFixed(2)),
        alerts: Math.abs(deviationPct) > 8
            ? [`Traffic deviation is ${deviationPct.toFixed(1)}% from forecast — review auto-scaling settings.`]
            : []
    };
}

/* ─── AUTH HELPERS ─────────────────────────────────────── */

async function checkAuth() {
    if (!window.supabaseClient) return null;
    try {
        const client = window.supabaseClient;
        let user = null;
        try {
            const { data: { session } } = await client.auth.getSession();
            user = session?.user || null;
        } catch (err) {
            console.warn("Supabase auth failed. Continuing to Demo Check:", err.message);
        }

        // ── Check Demo Bypass Fallback ──
        const demoEmail = localStorage.getItem('green_lambda_demo_user');
        if (!user && demoEmail) {
            user = { id: 'demo-user-123', email: demoEmail };
        }

        if (user) {
            // Check if local session has AWS functions. If not, try to fetch from DB.
            const localSession = getSession();
            if (!localSession?.functions?.length) {
                // DO NOT CRASH: Make sure to use the resolved client!
                // Also, if it's the demo-user-123, skip the DB lookup natively because they have no DB records!
                if (user.id === 'demo-user-123') {
                    // Do nothing for demo user, let them reach the Connect AWS page
                }
                // (Server Synchronization Disabled: The user must explicitly Connect AWS rather than downloading legacy tests)
            }
        }
        return user;
    } catch { return null; }
}

function initLoginPage() {
    // If already logged in, skip straight to dashboard
    checkAuth().then(user => {
        if (user) window.location.href = 'dashboard.html';
    });

    // ── Flip toggle (checkbox → rotateY) ────────────────
    const toggle = document.getElementById('authToggle');
    const flipCard = document.getElementById('flipCardInner');
    const labelLogin = document.getElementById('labelLogin');
    const labelSignup = document.getElementById('labelSignup');

    if (toggle && flipCard) {
        toggle.addEventListener('change', () => {
            const isSignup = toggle.checked;
            flipCard.classList.toggle('flipped', isSignup);
            labelLogin.classList.toggle('active', !isSignup);
            labelSignup.classList.toggle('active', isSignup);
        });
        // Also let clicking the labels toggle the switch
        labelLogin?.addEventListener('click', () => { toggle.checked = false; toggle.dispatchEvent(new Event('change')); });
        labelSignup?.addEventListener('click', () => { toggle.checked = true; toggle.dispatchEvent(new Event('change')); });
    }

    // ── Forgot password handler ──
    if (forgotBtn) {
        forgotBtn.addEventListener('click', async () => {
            const email = document.getElementById('loginEmail')?.value.trim();
            if (!email) { setBanner(loginStatus, 'error', 'Enter your email first.'); return; }
            setBanner(loginStatus, 'loading', 'Sending reset link\u2026');
            const { error } = await window.supabase.auth.resetPasswordForEmail(email, {
                redirectTo: window.location.origin + '/login.html'
            });
            if (error) setBanner(loginStatus, 'error', error.message);
            else setBanner(loginStatus, 'ok', 'Reset email sent! Check your inbox.');
        });
    }

    // ── Signup form (back face of flip card) ───────────────
    const signupForm = document.getElementById('signupForm');
    const signupStatus = document.getElementById('signupStatus');
    const signupSubmit = document.getElementById('signupSubmitBtn');

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('signupEmail').value.trim();
            const password = document.getElementById('signupPassword').value;
            signupSubmit.disabled = true;
            setBanner(signupStatus, 'loading', 'Creating account\u2026');
            try {
                if (!window.supabase) throw new Error('Supabase not initialised.');
                const { data, error } = await window.supabase.auth.signUp({ email, password });
                if (error) throw error;
                if (data.user) {
                    await window.supabase.from('profiles').upsert([{ id: data.user.id, email: data.user.email }]);
                }
                setBanner(signupStatus, 'ok', 'Account created! Redirecting\u2026');
                setTimeout(() => window.location.href = 'dashboard.html', 1800);
            } catch (err) {
                setBanner(signupStatus, 'error', err.message || 'Sign-up failed.');
                signupSubmit.disabled = false;
            }
        });
    }
}

/* ─── FUNCTION LIST RENDERER ───────────────────────────── */

function renderFunctionList(functions, listEl, countEl) {
    if (!listEl || !countEl) return;

    listEl.innerHTML = '';
    countEl.textContent = `${functions.length} functions`;

    functions.forEach((fn) => {
        const item = document.createElement('div');
        item.className = 'function-item';
        item.innerHTML = `
            <span class="function-item-name">${fn.name}</span>
            <span class="function-item-meta">${fn.runtime} • ${fn.memoryMb} MB</span>
        `;
        listEl.appendChild(item);
    });
}

async function initConnectPage() {
    // Auth guard — redirect unauthenticated users to the login page
    const user = await checkAuth();
    if (!user) {
        window.location.href = 'login.html';
        return;
    }

    const form = document.getElementById('connectAwsForm');
    const status = document.getElementById('connectStatus');
    const wrap = document.getElementById('connectedFunctionsWrap');
    const list = document.getElementById('functionList');
    const count = document.getElementById('functionCount');
    const connectBtn = document.getElementById('connectAwsBtn');

    if (!form) return;

    const existing = getSession();
    const instructionsInfo = document.getElementById('awsInstructions');

    if (existing?.functions?.length) {
        if (instructionsInfo) instructionsInfo.style.display = 'none';
        wrap.hidden = false;
        renderFunctionList(existing.functions, list, count);
        setBanner(status, 'ok', `Your AWS connection was loaded securely from your account! You can go straight to Analysis, or reconnect to refresh your functions.`);
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const payload = {
            accessKeyId: document.getElementById('awsAccessKey')?.value?.trim(),
            secretAccessKey: document.getElementById('awsSecretKey')?.value?.trim(),
            sessionToken: document.getElementById('awsSessionToken')?.value?.trim(),
            region: document.getElementById('awsRegion')?.value,
            accountAlias: document.getElementById('awsAccountAlias')?.value?.trim()
        };

        if (!payload.accessKeyId || !payload.secretAccessKey || !payload.region) {
            setBanner(status, 'error', 'Access key, secret key, and region are required.');
            return;
        }

        connectBtn.disabled = true;
        setBanner(status, 'loading', 'Connecting to AWS and discovering Lambda functions...');

        let response;
        let mode = 'live';

        try {
            response = await apiRequest('/connect-aws', { method: 'POST', body: payload });
        } catch (error) {
            mode = 'demo';
            response = createDemoConnection(payload.region);
            setBanner(status, 'ok', `Simulation Mode Active: Securely loading demonstration AWS connections.`);
        }

        const functions = normalizeFunctions(response.functions || response.lambdaFunctions || []);

        const session = {
            connectionId: response.connectionId || response.connection_id || `local-${Date.now()}`,
            region: response.region || payload.region,
            accountAlias: payload.accountAlias || response.accountAlias || '',
            mode,
            functions,
            connectedAt: new Date().toISOString()
        };

        // --- SUPABASE: Save Connection and Lambda Functions ---
        const client = window.supabaseClient;
        if (client && user && user.id !== 'demo-user-123') {
            try {
                // 1. Insert into aws_connections
                const { data: connData, error: connErr } = await client
                    .from('aws_connections')
                    .insert([{
                        user_id: user.id,
                        account_alias: session.accountAlias || 'GreenLambda Demo Account',
                        region: session.region || 'ap-south-1'
                    }])
                    .select();

                if (connErr) throw connErr;

                const dbConnId = connData[0].id;
                session.dbConnectionId = dbConnId; // Save this ID in local session for later

                // 2. Insert into lambda_functions
                if (functions.length > 0) {
                    const fnInserts = functions.map(fn => ({
                        connection_id: dbConnId,
                        function_name: fn.name,
                        runtime: fn.runtime || 'nodejs18.x',
                        memory_mb: fn.memoryMb || 128
                    }));

                    const { error: fnErr } = await client
                        .from('lambda_functions')
                        .insert(fnInserts);

                    if (fnErr) throw fnErr;
                }
                console.log("✅ Successfully saved AWS connection & functions to Supabase!");
            } catch (err) {
                console.error("❌ Supabase Save Error:", err);
                setBanner(status, 'warn', `Saved locally, but failed to save to database: ${err.message}`);
            }
        }

        setSession(session);

        // Save credentials to localStorage so runtime-test and other pages
        // can make live CloudWatch calls directly.
        if (mode === 'live') {
            localStorage.setItem('gl_ak', payload.accessKeyId);
            localStorage.setItem('gl_sk', payload.secretAccessKey);
            if (payload.sessionToken) localStorage.setItem('gl_st', payload.sessionToken);
            localStorage.setItem('gl_region', payload.region);
            console.log('✅ AWS credentials saved to localStorage for live session.');
        } else {
            localStorage.removeItem('gl_ak');
            localStorage.removeItem('gl_sk');
            localStorage.removeItem('gl_st');
        }
        if (instructionsInfo) instructionsInfo.style.display = 'none';
        wrap.hidden = false;
        renderFunctionList(functions, list, count);

        if (mode === 'live') {
            setBanner(status, 'ok', `AWS connected successfully. ${functions.length} Lambda function(s) discovered.`);
        }

        connectBtn.disabled = false;
    });
}

function initAnalyzePage() {
    const session = getSession();
    const hint = document.getElementById('analyzeConnectionHint');
    const form = document.getElementById('analyzeFunctionForm');
    const fnSelect = document.getElementById('functionSelect');
    const baselineInput = document.getElementById('baselineTraffic');
    const modelBar = document.getElementById('modelSelectorBar');
    const predictionPanel = document.getElementById('predictionPanel');
    const spikeHint = document.getElementById('spikeHint');
    const spikeForm = document.getElementById('spikeForm');
    const spikePanel = document.getElementById('spikeResultPanel');

    if (!form || !fnSelect || !baselineInput || !modelBar) return;

    if (!session?.functions?.length) {
        setBanner(hint, 'warn', 'No AWS session found. Connect your AWS account first on the Connect page.');
        form.querySelectorAll('input, select, button').forEach((el) => {
            el.disabled = true;
        });
        if (spikeForm) {
            spikeForm.querySelectorAll('input, select, button').forEach((el) => {
                el.disabled = true;
            });
        }
        return;
    }

    setBanner(hint, 'ok', `Connected to ${session.region}. Choose a function to begin analysis.`);

    session.functions.forEach((fn) => {
        const option = document.createElement('option');
        option.value = fn.name;
        option.textContent = `${fn.name} (${fn.runtime})`;
        fnSelect.appendChild(option);
    });

    let activeModel = 'xgboost';
    modelBar.querySelectorAll('.ms-btn').forEach((button) => {
        button.addEventListener('click', () => {
            modelBar.querySelectorAll('.ms-btn').forEach((other) => other.classList.remove('active'));
            button.classList.add('active');
            activeModel = button.dataset.model || 'xgboost';
        });
    });

    let latestAnalysis = getStoredJson(GREENLAMBDA_KEYS.analysis) || null;
    let spikeChart = null;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const functionName = fnSelect.value;
        const baselineRph = Number(baselineInput.value || 0);

        if (!functionName || !baselineRph) {
            setBanner(hint, 'error', 'Select a function and enter baseline traffic to continue.');
            return;
        }

        setBanner(hint, 'loading', 'Running ML prediction for selected function...');

        let response;
        let mode = 'live';

        try {
            response = await apiRequest('/analyze-function', {
                method: 'POST',
                body: {
                    connectionId: session.connectionId,
                    functionName,
                    model: activeModel,
                    baselineRph
                }
            });
        } catch (error) {
            mode = 'demo';
            response = createDemoAnalysis({ baselineRph, functionName, model: activeModel });
            setBanner(hint, 'ok', `Simulation Mode Active: Generating High-Fidelity ML Prediction Analysis locally.`);
        }

        const energyWhPerInvocation = Number(
            response.energyWhPerInvocation ||
            response.energy_per_invocation_wh ||
            response.energy_target_wh ||
            0
        );
        const confidence = Number(response.confidence || response.modelConfidence || 0.9);
        const monthlyInvocations = Number(response.monthlyInvocations || (baselineRph * 24 * 30));
        const monthlyCarbonKg = Number(
            response.monthlyCarbonKg ||
            response.carbonKg ||
            (((monthlyInvocations * energyWhPerInvocation) / 1000) * 0.5)
        );
        const monthlyCostInr = Number(
            response.monthlyCostInr ||
            response.costInr ||
            (((monthlyInvocations * energyWhPerInvocation) / 1000) * 8.4)
        );

        latestAnalysis = {
            functionName,
            baselineRph,
            model: activeModel,
            mode,
            energyWhPerInvocation,
            confidence,
            monthlyInvocations,
            monthlyCarbonKg,
            monthlyCostInr,
            analyzedAt: new Date().toISOString()
        };

        // --- SUPABASE: Save ML Analysis ---
        if (window.supabase && session?.dbConnectionId) {
            try {
                const { data: fnData } = await window.supabase
                    .from('lambda_functions')
                    .select('id')
                    .eq('connection_id', session.dbConnectionId)
                    .eq('function_name', functionName)
                    .single();

                if (fnData) {
                    const { data: analysisData, error: anErr } = await window.supabase
                        .from('ml_analysis')
                        .insert([{
                            function_id: fnData.id,
                            model_used: activeModel,
                            baseline_rph: baselineRph,
                            energy_wh: energyWhPerInvocation,
                            confidence: confidence,
                            monthly_invocations: monthlyInvocations,
                            monthly_carbon_kg: monthlyCarbonKg,
                            monthly_cost_inr: monthlyCostInr
                        }])
                        .select();

                    if (!anErr && analysisData) {
                        latestAnalysis.dbAnalysisId = analysisData[0].id; // Save for spike forecast
                        console.log("✅ ML Analysis saved to Supabase!");
                    }
                }
            } catch (err) {
                console.error("❌ Supabase Analysis Save Error:", err);
            }
        }

        setStoredJson(GREENLAMBDA_KEYS.analysis, latestAnalysis);

        document.getElementById('selectedFnLabel').textContent = `Function: ${functionName}`;
        document.getElementById('predEnergy').innerHTML = `${energyWhPerInvocation.toFixed(3)} <span class="result-unit">Wh</span>`;
        document.getElementById('predConfidence').textContent = `Confidence: ${(confidence * 100).toFixed(1)}%`;
        document.getElementById('predCarbon').innerHTML = `${monthlyCarbonKg.toFixed(2)} <span class="result-unit">kg CO₂</span>`;
        document.getElementById('predCost').textContent = formatCurrencyInr(monthlyCostInr);
        document.getElementById('predInvocations').textContent = formatNumber(monthlyInvocations);
        predictionPanel.removeAttribute('hidden');
        predictionPanel.style.display = 'block';

        if (mode === 'live') {
            setBanner(hint, 'ok', 'Function analysis complete. Use spike simulator for event forecasting.');
        }
    });

    const presetRow = document.getElementById('spikePresetRow');
    const multiplierInput = document.getElementById('trafficMultiplier');
    if (presetRow && multiplierInput) {
        presetRow.querySelectorAll('.chip').forEach((chip) => {
            chip.addEventListener('click', () => {
                presetRow.querySelectorAll('.chip').forEach((other) => other.classList.remove('active'));
                chip.classList.add('active');
                multiplierInput.value = chip.dataset.multiplier || '20';
            });
        });
    }

    if (spikeForm) {
        spikeForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            if (!latestAnalysis) {
                setBanner(spikeHint, 'error', 'Run function analysis before predicting spike impact.');
                return;
            }

            const multiplier = Number(document.getElementById('trafficMultiplier')?.value || 20);
            const durationHours = Number(document.getElementById('spikeDurationHours')?.value || 72);

            setBanner(spikeHint, 'loading', 'Generating spike forecast...');

            let response;
            let mode = 'live';

            try {
                response = await apiRequest('/predict-spike', {
                    method: 'POST',
                    body: {
                        connectionId: session.connectionId,
                        functionName: latestAnalysis.functionName,
                        model: latestAnalysis.model,
                        baselineRph: latestAnalysis.baselineRph,
                        multiplier,
                        durationHours
                    }
                });
            } catch (error) {
                mode = 'demo';
                response = createDemoSpike({ baselineRph: latestAnalysis.baselineRph, multiplier, durationHours }, latestAnalysis);
                setBanner(spikeHint, 'ok', `Simulation Mode Active: Rendering programmatic hour-by-hour Spike Forecast.`);
            }

            const totals = response.totals || {};
            const hourly = Array.isArray(response.hourly) ? response.hourly : [];

            const energyKwh = Number(totals.energyKwh || totals.totalEnergyKwh || 0);
            const carbonKg = Number(totals.carbonKg || totals.totalCarbonKg || 0);
            const costInr = Number(totals.costInr || totals.totalCostInr || 0);
            const peakReqPerHour = Number(totals.peakReqPerHour || (latestAnalysis.baselineRph * multiplier));

            document.getElementById('spikeEnergy').innerHTML = `${energyKwh.toFixed(3)} <span class="result-unit">kWh</span>`;
            document.getElementById('spikeCarbon').innerHTML = `${carbonKg.toFixed(3)} <span class="result-unit">kg CO₂</span>`;
            document.getElementById('spikeCost').textContent = formatCurrencyInr(costInr);
            document.getElementById('spikePeakReq').textContent = formatNumber(peakReqPerHour);
            spikePanel.removeAttribute('hidden');
            spikePanel.style.display = 'block';

            // Auto-scroll the page down so the user is forced to see it!
            setTimeout(() => {
                spikePanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);

            setStoredJson(GREENLAMBDA_KEYS.forecast, {
                functionName: latestAnalysis.functionName,
                predictedReqPerHour: peakReqPerHour,
                durationHours,
                generatedAt: new Date().toISOString(),
                mode,
                totals: { energyKwh, carbonKg, costInr },
                hourly
            });

            // --- SUPABASE: Save Spike Forecast ---
            if (window.supabase && latestAnalysis.dbAnalysisId) {
                try {
                    const { error: spikeErr } = await window.supabase
                        .from('spike_forecasts')
                        .insert([{
                            analysis_id: latestAnalysis.dbAnalysisId,
                            multiplier: multiplier,
                            duration_hours: durationHours,
                            peak_req_per_hour: peakReqPerHour,
                            total_energy_kwh: energyKwh,
                            total_carbon_kg: carbonKg,
                            total_cost_inr: costInr,
                            forecast_data: hourly
                        }]);
                    if (!spikeErr) {
                        console.log("✅ Spike forecast saved to Supabase!");
                    } else {
                        throw spikeErr;
                    }
                } catch (err) {
                    console.error("❌ Supabase Spike Save Error:", err);
                }
            }

            const chartCanvas = document.getElementById('spikeForecastChart');
            if (typeof Chart !== 'undefined' && chartCanvas) {
                const labels = hourly.map((item) => `H${item.hour}`);
                const reqData = hourly.map((item) => Number(item.predictedReqPerHour || item.reqPerHour || 0));
                const energyData = hourly.map((item) => Number(item.predictedEnergyKwh || item.energyKwh || 0));

                if (spikeChart) spikeChart.destroy();

                spikeChart = new Chart(chartCanvas, {
                    type: 'line',
                    data: {
                        labels,
                        datasets: [
                            {
                                label: 'Req/Hour',
                                data: reqData,
                                borderColor: '#c8ff00',
                                backgroundColor: 'rgba(200,255,0,0.06)',
                                yAxisID: 'yReq',
                                tension: 0.35,
                                borderWidth: 2,
                                pointRadius: 0
                            },
                            {
                                label: 'Energy kWh',
                                data: energyData,
                                borderColor: '#7b61ff',
                                backgroundColor: 'rgba(123,97,255,0.06)',
                                yAxisID: 'yEnergy',
                                tension: 0.35,
                                borderWidth: 2,
                                pointRadius: 0
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { labels: { color: '#8a8a8a' } }
                        },
                        scales: {
                            x: { ticks: { color: '#555' }, grid: { color: 'rgba(255,255,255,0.03)' } },
                            yReq: {
                                position: 'left',
                                ticks: { color: '#8a8a8a' },
                                grid: { color: 'rgba(255,255,255,0.03)' }
                            },
                            yEnergy: {
                                position: 'right',
                                ticks: { color: '#8a8a8a' },
                                grid: { drawOnChartArea: false }
                            }
                        }
                    }
                });
            }

            if (mode === 'live') {
                setBanner(hint, 'ok', 'Spike forecast generated successfully. Open live monitoring dashboard next.');
            }
        });
    }
}

function initDashboardPage() {
    const session = getSession();
    const hint = document.getElementById('liveConnectionHint');
    const fnSelect = document.getElementById('liveFunctionSelect');
    const refreshIntervalSelect = document.getElementById('liveRefreshInterval');
    const autoToggle = document.getElementById('liveAutoToggle');
    const refreshNowBtn = document.getElementById('liveRefreshNowBtn');
    const alertBox = document.getElementById('liveAlertBox');

    if (!fnSelect || !refreshIntervalSelect || !autoToggle || !refreshNowBtn) return;

    if (!session?.functions?.length) {
        setBanner(hint, 'warn', 'No AWS session found. Connect and analyze a function first.');
        fnSelect.disabled = true;
        refreshNowBtn.disabled = true;
        return;
    }

    setBanner(hint, 'ok', `Monitoring enabled for ${session.region}. Choose a function to start.`);
    session.functions.forEach((fn) => {
        const option = document.createElement('option');
        option.value = fn.name;
        option.textContent = `${fn.name} (${fn.runtime})`;
        fnSelect.appendChild(option);
    });

    const forecast = getStoredJson(GREENLAMBDA_KEYS.forecast);
    if (forecast?.functionName) {
        fnSelect.value = forecast.functionName;
    }

    const compareCanvas = document.getElementById('liveCompareChart');
    const volumeCanvas = document.getElementById('liveInvocationChart');
    const sampleBody = document.getElementById('liveSampleBody');

    let compareChart = null;
    let volumeChart = null;
    let timer = null;

    if (typeof Chart !== 'undefined' && compareCanvas && volumeCanvas) {
        compareChart = new Chart(compareCanvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Predicted', data: [], borderColor: '#c8ff00', borderWidth: 2, tension: 0.35, pointRadius: 0 },
                    { label: 'Actual', data: [], borderColor: '#7b61ff', borderWidth: 2, tension: 0.35, pointRadius: 0 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#555' }, grid: { color: 'rgba(255,255,255,0.03)' } },
                    y: { ticks: { color: '#8a8a8a' }, grid: { color: 'rgba(255,255,255,0.03)' } }
                }
            }
        });

        volumeChart = new Chart(volumeCanvas, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{ label: 'Actual Req/Hr', data: [], backgroundColor: 'rgba(54,249,174,0.5)', borderRadius: 4 }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#555' }, grid: { color: 'rgba(255,255,255,0.03)' } },
                    y: { ticks: { color: '#8a8a8a' }, grid: { color: 'rgba(255,255,255,0.03)' } }
                }
            }
        });
    }

    const historyPoints = [];

    function pushHistory(point) {
        historyPoints.push(point);
        if (historyPoints.length > 12) historyPoints.shift();

        if (compareChart) {
            compareChart.data.labels = historyPoints.map((item) => item.timeLabel);
            compareChart.data.datasets[0].data = historyPoints.map((item) => item.predicted);
            compareChart.data.datasets[1].data = historyPoints.map((item) => item.actual);
            compareChart.update();
        }

        if (volumeChart) {
            volumeChart.data.labels = historyPoints.map((item) => item.timeLabel);
            volumeChart.data.datasets[0].data = historyPoints.map((item) => item.actual);
            volumeChart.update();
        }

        if (sampleBody) {
            sampleBody.innerHTML = '';
            [...historyPoints].reverse().forEach((item) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.timeStamp}</td>
                    <td>${formatNumber(item.predicted)}</td>
                    <td>${formatNumber(item.actual)}</td>
                    <td>${item.deviationPct.toFixed(2)}%</td>
                    <td><span class="badge ${item.statusClass}">${item.statusText}</span></td>
                `;
                sampleBody.appendChild(tr);
            });
        }
    }

    async function refreshLiveMetrics() {
        const functionName = fnSelect.value;
        if (!functionName) {
            setBanner(hint, 'warn', 'Select a function to fetch live metrics.');
            return;
        }

        setBanner(hint, 'loading', 'Fetching latest CloudWatch metrics...');

        let response;
        let mode = 'live';

        try {
            const forecastInfo = getStoredJson(GREENLAMBDA_KEYS.forecast) || {};
            const activeBaseline = forecastInfo.predictedReqPerHour || forecastInfo.baselineRph || 10000;
            
            response = await apiRequest(`/live-metrics?${toQuery({
                connectionId: session.connectionId,
                functionName,
                baselineRph: activeBaseline
            })}`);
        } catch (error) {
            mode = 'demo';
            const predicted = getStoredJson(GREENLAMBDA_KEYS.forecast)?.predictedReqPerHour || 200000;
            response = createDemoLiveMetrics(predicted);
            setBanner(hint, 'warn', `Backend unavailable (${error.message}). Showing demo live metrics.`);
        }

        const predicted = Number(response.predictedReqPerHour || response.predicted || 0);
        const actual = Number(response.actualReqPerHour || response.actual || 0);
        const deviationPct = Number(response.deviationPct || (((actual - predicted) / Math.max(predicted, 1)) * 100));

        const statusText = Math.abs(deviationPct) <= 8 ? 'On Track' : 'Drifting';
        const statusClass = Math.abs(deviationPct) <= 8 ? 'optimal' : 'warning';

        document.getElementById('liveKpiPredicted').textContent = formatNumber(predicted);
        document.getElementById('liveKpiActual').textContent = formatNumber(actual);
        document.getElementById('liveKpiDeviation').textContent = `${deviationPct.toFixed(2)}%`;
        document.getElementById('liveKpiStatus').textContent = statusText;
        document.getElementById('liveLastUpdated').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;

        const alerts = Array.isArray(response.alerts) ? response.alerts : [];
        if (alerts.length) {
            setBanner(alertBox, 'warn', alerts[0]);
        } else {
            setBanner(alertBox, 'ok', 'No critical deviation. Forecast is within safe limits.');
        }

        updateOptimizationAlerts(deviationPct, predicted, actual, fnSelect.value);

        pushHistory({
            predicted,
            actual,
            deviationPct,
            statusText,
            statusClass,
            timeLabel: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            timeStamp: new Date().toLocaleString()
        });

        if (mode === 'live') {
            setBanner(hint, 'ok', 'Live metrics updated successfully.');
        }
    }

    function resetAutoRefresh() {
        if (timer) {
            clearInterval(timer);
            timer = null;
        }

        if (autoToggle.value === 'on') {
            const seconds = Number(refreshIntervalSelect.value || 60);
            timer = setInterval(refreshLiveMetrics, seconds * 1000);
        }
    }

    refreshNowBtn.addEventListener('click', refreshLiveMetrics);
    fnSelect.addEventListener('change', refreshLiveMetrics);
    refreshIntervalSelect.addEventListener('change', resetAutoRefresh);
    autoToggle.addEventListener('change', resetAutoRefresh);

    if (fnSelect.value) {
        refreshLiveMetrics();
    }
    resetAutoRefresh();
}

/* --- Optimization Alerts Logic --- */
function updateOptimizationAlerts(deviationPct, predicted, actual, functionName) {
    const body = document.getElementById('optimizationAlertBody');
    if (!body) return;
    body.innerHTML = '';

    const abs = Math.abs(deviationPct);
    const isOver = actual > predicted;
    const alerts = [];

    // Map severities to visual payloads perfectly matching analyze.html UI
    const severities = {
        ok: { color: 'rgba(100,255,120,0.1)', border: 'rgba(100,255,120,0.35)', icon: '🟢' },
        warning: { color: 'rgba(255,200,0,0.1)', border: 'rgba(255,200,0,0.35)', icon: '🟡' },
        critical: { color: 'rgba(255,80,80,0.12)', border: 'rgba(255,80,80,0.4)', icon: '🔴' }
    };

    if (abs <= 8) {
        alerts.push({ 
            sev: 'ok', 
            title: 'System Healthy', 
            detail: `Actual traffic (<strong>${formatNumber(actual)} req/hr</strong>) is within <strong>${abs.toFixed(1)}%</strong> of forecast.`, 
            fix: 'No networking adjustment needed. CloudWatch tracking remains fully optimal.' 
        });
    } else if (abs > 8 && abs <= 20) {
        alerts.push({ 
            sev: 'warning', 
            title: `Mild Drift Detected (${deviationPct.toFixed(1)}%)`, 
            detail: isOver ? 'Actual live traffic slightly exceeds ML forecasting.' : 'Traffic volume is idling below ML forecast.', 
            fix: isOver ? `Consider enabling AWS Lambda Provisioned Concurrency on <strong>"${functionName}"</strong> to aggressively fight cold-start latency.` : 'Scale down the function\'s reserved memory configuration to slash idle compute cost.' 
        });
    } else if (abs > 20 && abs <= 40) {
        alerts.push({ 
            sev: 'critical', 
            title: `Significant Anomaly (${deviationPct.toFixed(1)}%)`, 
            detail: isOver ? 'Traffic dramatically exceeds baseline forecasting constraints.' : 'Traffic severely under-utilizing baseline compute.',
            fix: isOver ? `Estimated cost hike: <strong>~₹${Math.round((abs / 100) * 2400)}</strong>. Enable CloudWatch Alarms immediately on "Throttles".` : `Your Lambda is heavily over-provisioned. Downsizing memory could save <strong>~₹${Math.round((abs / 100) * 1200)}/month</strong>.` 
        });
    } else {
        alerts.push({ 
            sev: 'critical', 
            title: `Critical Deviation (${deviationPct.toFixed(1)}%)`,
            detail: 'Serverless telemetry has completely detached from predictive forecasting models.',
            fix: isOver ? `<strong>DDoS Risk:</strong> Burst anomaly may rack up <strong>₹${Math.round((abs / 100) * 6000)}+</strong>. Enable AWS WAF shielding immediately!` : `<strong>Dead Traffic:</strong> Check if your Lambda trigger (API Gateway, SQS, etc.) is misconfigured or completely inactive.`
        });
    }

    alerts.forEach(a => {
        const div = document.createElement('div');
        div.style.cssText = `background: ${severities[a.sev].color}; border: 1px solid ${severities[a.sev].border}; border-radius: 10px; padding: 1rem 1.2rem;`;
        div.innerHTML = `
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
                <span style="font-size:1rem;">${severities[a.sev].icon}</span>
                <strong style="color:rgba(255,255,255,0.95); font-size:0.95rem;">${a.title}</strong>
            </div>
            <p style="margin:0 0 0.5rem; color:rgba(255,255,255,0.7); font-size:0.87rem; line-height:1.5;">${a.detail}</p>
            <p style="margin:0; color:rgba(255,255,255,0.55); font-size:0.83rem; line-height:1.5;"><strong style="color:rgba(255,255,255,0.75);">Fix:</strong> ${a.fix}</p>
        `;
        body.appendChild(div);
    });
}

/* --- Login Page Logic --- */
function initLoginPage() {
    const authToggle = document.getElementById('authToggle');
    const flipCardInner = document.getElementById('flipCardInner');
    const labelLogin = document.getElementById('labelLogin');
    const labelSignup = document.getElementById('labelSignup');

    if (authToggle) {
        authToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                // Switching to Sign up
                flipCardInner.classList.add('flipped');
                labelLogin.classList.remove('active');
                labelSignup.classList.add('active');
            } else {
                // Switching to Log in
                flipCardInner.classList.remove('flipped');
                labelSignup.classList.remove('active');
                labelLogin.classList.add('active');
            }
        });

        labelLogin.addEventListener('click', () => {
            if (authToggle.checked) {
                authToggle.checked = false;
                authToggle.dispatchEvent(new Event('change'));
            }
        });
        labelSignup.addEventListener('click', () => {
            if (!authToggle.checked) {
                authToggle.checked = true;
                authToggle.dispatchEvent(new Event('change'));
            }
        });
    }

    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginStatus = document.getElementById('loginStatus');
    const signupStatus = document.getElementById('signupStatus');

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const btn = document.getElementById('signupSubmitBtn');

            signupStatus.textContent = 'Creating account...';
            signupStatus.className = 'fc-status loading';
            btn.disabled = true;

            try {
                const { data, error } = await window.supabaseClient.auth.signUp({
                    email: email,
                    password: password,
                });

                if (error) {
                    signupStatus.textContent = error.message || 'Error occurred';
                    signupStatus.className = 'fc-status error';
                    btn.disabled = false;
                } else {
                    signupStatus.textContent = 'Account created successfully!';
                    signupStatus.className = 'fc-status ok';
                    signupForm.reset();
                    setTimeout(() => {
                        authToggle.checked = false;
                        authToggle.dispatchEvent(new Event('change'));
                        btn.disabled = false;
                        signupStatus.textContent = '';
                    }, 1500);
                }
            } catch (err) {
                console.error("Signup exception:", err);
                let msg = err.message || JSON.stringify(err);
                if (msg.includes("supabase is not defined")) {
                    msg = "Connection blocked. Check your AdBlocker or internet connection.";
                }
                signupStatus.textContent = 'Error: ' + msg;
                signupStatus.className = 'fc-status error';
                btn.disabled = false;
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const btn = document.getElementById('loginSubmitBtn');

            loginStatus.textContent = 'Logging in...';
            loginStatus.className = 'fc-status loading';
            btn.disabled = true;

            try {
                // 1. Smart Dummy Email Detection
                const dummyKeywords = ['demo@', 'test@', 'dummy@', '@example.com', '@test.com'];
                const isDummyEmail = dummyKeywords.some(keyword => email.toLowerCase().includes(keyword));

                if (isDummyEmail) {
                    loginStatus.textContent = "Presentation Override: Securely connecting Offline Mode...";
                    loginStatus.className = 'fc-status ok';
                    localStorage.removeItem('greenlambda.session');
                    localStorage.removeItem('greenlambda.analysis');
                    localStorage.removeItem('greenlambda.forecast');
                    localStorage.setItem('green_lambda_demo_user', email);
                    setTimeout(() => window.location.href = 'index.html', 1200);
                    return;
                }

                // 2. Legitimate Cloud Authentication Route
                const { data, error } = await window.supabaseClient.auth.signInWithPassword({
                    email: email,
                    password: password,
                });

                if (error) {
                    loginStatus.textContent = error.message;
                    loginStatus.className = 'fc-status error';
                    btn.disabled = false;
                } else {
                    // SECURE PURGE: Completely destroy any leftover caches from previous Demo sessions or alternate users
                    // so the new legitimate user gets a 100% clean profile.
                    localStorage.removeItem('greenlambda.session');
                    localStorage.removeItem('greenlambda.analysis');
                    localStorage.removeItem('greenlambda.forecast');
                    localStorage.removeItem('green_lambda_demo_user');

                    loginStatus.textContent = 'Success! Redirecting...';
                    loginStatus.className = 'fc-status ok';
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 500);
                }
            } catch (err) {
                console.error("Login exception:", err);
                let msg = err.message || JSON.stringify(err);
                if (msg.includes("supabase is not defined")) msg = "Connection blocked (check AdBlocker).";
                loginStatus.textContent = 'Error: ' + msg;
                loginStatus.className = 'fc-status error';
                btn.disabled = false;
            }
        });
    }
}

/* --- Global Session Checker for UI Profile Avatar --- */
async function checkAuthStatus() {
    if (!window.supabaseClient) return;

    try {
        let session = null;
        let activeUserEmail = null;

        if (window.supabaseClient) {
            try {
                const res = await window.supabaseClient.auth.getSession();
                session = res.data.session;
            } catch (err) {
                console.warn("Supabase getSession failed, continuing local check:", err.message);
            }
        }

        // ── Check Demo Bypass Fallback ──
        const demoEmail = localStorage.getItem('green_lambda_demo_user');

        if (session && session.user) {
            activeUserEmail = session.user.email;
        } else if (demoEmail) {
            session = true; // Mock true to force UI update
            activeUserEmail = demoEmail;
        }

        // This targets the specific Get Started button on index.html, dashboard.html, etc.
        const authBtnProfile = document.getElementById('authBtnProfile');
        const authBtnInner = document.getElementById('authBtnInner');
        const homeConnectAwsBtn = document.getElementById('homeConnectAwsBtn');

        // If a session exists, we swap the UI!
        if (session) {

            // Re-route the bottom CTA directly to AWS dashboard since they are logged in!
            if (homeConnectAwsBtn) {
                homeConnectAwsBtn.href = 'connect.html';
                // Update icon/text optionally, but default says 'Connect AWS' which is correct
            }

            if (authBtnProfile && authBtnInner) {

                // Extract their email prefix to use as a username
                const username = (activeUserEmail || "verified").split('@')[0];

                // 1. Hide the entire "Get Started" button completely
                authBtnProfile.style.display = 'none';

                // 2. Check if avatar already exists (to avoid duplicate injection on redraws)
                if (!document.getElementById('greenLambdaAvatar')) {
                    // Create a container specifically for the avatar + dropdown relative positioning
                    const avatarContainer = document.createElement('div');
                    avatarContainer.id = 'greenLambdaAvatarContainer';
                    avatarContainer.style.position = 'relative';

                    // 3. Create a modern circular Profile Avatar
                    const avatarBtn = document.createElement('div');
                    avatarBtn.id = 'greenLambdaAvatar';
                    avatarBtn.title = `Logged in as ${username}`;
                    avatarBtn.style.cssText = `
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: linear-gradient(145deg, #c8ff00, #00f0ff);
                    color: #0a0a0a;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 800;
                    font-size: 1.1rem;
                    text-transform: uppercase;
                    box-shadow: 0 0 12px rgba(200,255,0,0.5);
                    cursor: pointer;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                `;

                    // Set the initial of their username inside the circle
                    avatarBtn.textContent = username.charAt(0);

                    // Add hover animations
                    avatarBtn.onmouseover = () => { avatarBtn.style.boxShadow = '0 0 20px rgba(0,240,255,0.7)'; };
                    avatarBtn.onmouseout = () => { avatarBtn.style.boxShadow = '0 0 12px rgba(200,255,0,0.5)'; };

                    // 4. Create the Dropdown Popup Menu
                    const dropdown = document.createElement('div');
                    dropdown.id = 'greenLambdaDropdown';
                    dropdown.style.cssText = `
                    position: absolute;
                    top: 50px;
                    right: 0;
                    width: 200px;
                    background: #111;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.8);
                    display: none;
                    flex-direction: column;
                    z-index: 9999;
                    overflow: hidden;
                    animation: fadeIn 0.15s ease-out;
                `;

                    // Add Dropdown Items
                    dropdown.innerHTML = `
                    <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <div style="font-size: 0.8rem; color: #888;">Signed in as</div>
                        <div style="font-size: 0.9rem; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${activeUserEmail}</div>
                    </div>
                    <a href="connect.html" style="padding: 12px 16px; text-decoration: none; color: #e0e0e0; font-size: 0.9rem; transition: background 0.2s;">
                        ⚡ Dashboard
                    </a>
                    <div id="logoutBtnWrapper" style="padding: 12px 16px; border-top: 1px solid rgba(255,255,255,0.05); color: #ff4a4a; font-size: 0.9rem; cursor: pointer; transition: background 0.2s;">
                        🚪 Log Out
                    </div>
                `;

                    // Assemble the DOM payload
                    avatarContainer.appendChild(avatarBtn);
                    avatarContainer.appendChild(dropdown);

                    // Inject it directly next to where the Get Started button was!
                    authBtnProfile.parentNode.insertBefore(avatarContainer, authBtnProfile.nextSibling);

                    // CSS styling for dropdown hover states dynamically
                    const style = document.createElement('style');
                    style.textContent = `
                    #greenLambdaDropdown a:hover, #logoutBtnWrapper:hover { background: rgba(255,255,255,0.05); }
                    @keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
                `;
                    document.head.appendChild(style);

                    // Toggle dropdown on avatar click
                    avatarBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const isVisible = dropdown.style.display === 'flex';
                        dropdown.style.display = isVisible ? 'none' : 'flex';
                    });

                    // Close dropdown if clicking anywhere else on the page
                    document.addEventListener('click', (e) => {
                        if (!avatarContainer.contains(e.target)) {
                            dropdown.style.display = 'none';
                        }
                    });

                    // Logout logic natively executed
                    document.getElementById('logoutBtnWrapper').addEventListener('click', async () => {
                        // SECURE PURGE: Completely destroy ALL mock data, cached AWS telemetry and credentials
                        localStorage.removeItem('green_lambda_demo_user');
                        localStorage.removeItem('greenlambda.session');
                        localStorage.removeItem('gl_ak');
                        localStorage.removeItem('gl_sk');
                        localStorage.removeItem('gl_st');
                        localStorage.removeItem('gl_region');

                        // Destroy real Supabase session natively
                        if (window.supabaseClient) {
                            try { await window.supabaseClient.auth.signOut(); } catch (e) { }
                        }

                        // Native UI Reset (Remove Avatar, Bring back "Get Started", Route Connect backwards)
                        avatarContainer.remove();
                        authBtnProfile.style.display = 'flex';
                        if (homeConnectAwsBtn) homeConnectAwsBtn.href = "login.html";
                    });
                }
            }
        } else {
            // User is explicitly logged out
            if (homeConnectAwsBtn) homeConnectAwsBtn.href = "login.html";
        }
    } catch (e) {
        // If they bypass normally or no connection is active, just leave it as Get Started
    }
}

// Ensure it checks auth on every single page load natively
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAuthStatus);
} else {
    checkAuthStatus();
}
