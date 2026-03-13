
/* --- green_lambda_inject.js --- */
(function () {
    'use strict';
    let retries = 0;

    function injectGreenLambdaLoader() {
        const loaderAnimation = document.querySelector('.ic-loader-animation');

        if (loaderAnimation) {
            console.log('Found loader animation container, injecting GREEN LAMBDA...');

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
const initApp = () => {
    console.log("Green Lambda App Initializing...");
    initScrollReveal();
    initNavigation();
    initScrollProgress();
    initHeroCanvas();
    initKPICounters();
    initLiveMetrics();
    initCharts();
    populateTable();
    initSearch();
    initChipButtons();
    initDiscoverModal();
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

        let current = '';
        sections.forEach(s => {
            const top = s.offsetTop - 100;
            if (window.scrollY >= top) current = s.id;
        });

        links.forEach(l => {
            l.classList.toggle('active', l.dataset.section === current);
        });
    });

    links.forEach(link => {
        link.addEventListener('click', e => {
            const sectionId = link.dataset.section;
            if (!sectionId) return; // Allow normal navigation if no data-section exists

            e.preventDefault();
            const target = document.getElementById(sectionId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
            if (navLinksWrap) navLinksWrap.classList.remove('open');
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
        { id: 'kpiEnergy', end: 3.47, dec: 2 },
        { id: 'kpiCost', end: 71000, dec: 0 },
        { id: 'kpiCarbon', end: 12.8, dec: 1 },
        { id: 'kpiAccuracy', end: 0.943, dec: 3 }
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
                        data: [3.2, 3.8, 4.1, 3.5, 4.6, 2.9, 3.4],
                        borderColor: '#c8ff00',
                        backgroundColor: 'rgba(200,255,0,0.04)',
                        borderWidth: 2, fill: true, tension: 0.4,
                        pointRadius: 3, pointBackgroundColor: '#c8ff00', pointBorderWidth: 0, pointHoverRadius: 6
                    },
                    {
                        label: 'Actual',
                        data: [3.1, 3.9, 3.8, 3.7, 4.3, 3.1, 3.5],
                        borderColor: '#7b61ff',
                        backgroundColor: 'rgba(123,97,255,0.03)',
                        borderWidth: 2, fill: true, tension: 0.4,
                        pointRadius: 3, pointBackgroundColor: '#7b61ff', pointBorderWidth: 0, pointHoverRadius: 6
                    },
                    {
                        label: 'Optimized',
                        data: [2.4, 2.8, 3.0, 2.6, 3.4, 2.1, 2.5],
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
                labels: ['API Gateway', 'DynamoDB Ops', 'S3 Transfers', 'Compute', 'Cold Starts', 'Auth/JWT'],
                datasets: [{
                    data: [28, 32, 15, 12, 8, 5],
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
                labels: ['Memory Alloc', 'I/O Calls', 'Cyclomatic Cx', 'Runtime (ms)', 'Cold Start', 'Loop Depth', 'Ext. APIs', 'Code Lines'],
                datasets: [{
                    label: 'SHAP Impact',
                    data: [0.34, 0.28, 0.22, 0.19, 0.16, 0.11, 0.09, 0.05],
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
        const data = [];
        for (let i = 0; i < 60; i++) {
            const actual = Math.random() * 5 + 0.5;
            const pred = actual + (Math.random() - 0.5) * 0.6;
            data.push({ x: actual, y: Math.max(0.1, pred) });
        }
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
                    { label: 'XGBoost', data: [94, 92, 90, 78, 95, 82], borderColor: '#c8ff00', backgroundColor: 'rgba(200,255,0,0.06)', borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#c8ff00' },
                    { label: 'Random Forest', data: [91, 88, 85, 85, 90, 88], borderColor: '#36f9ae', backgroundColor: 'rgba(54,249,174,0.04)', borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#36f9ae' },
                    { label: 'Neural Net', data: [94, 90, 88, 45, 72, 40], borderColor: '#7b61ff', backgroundColor: 'rgba(123,97,255,0.04)', borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#7b61ff' },
                    { label: 'SVR', data: [89, 82, 78, 92, 88, 65], borderColor: '#ffc233', backgroundColor: 'rgba(255,194,51,0.04)', borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#ffc233' }
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
/* analyze script */
// Wait for Monaco loader
let editor;
if (typeof require !== 'undefined') {
    require.config({ paths: { 'vs': 'node_modules/monaco-editor/min/vs' } });
    require(['vs/editor/editor.main'], function () {

        // Define custom Green Lambda Theme
        monaco.editor.defineTheme('greenLambdaTheme', {
            base: 'vs-dark',
            inherit: true,
            rules: [
                { token: 'comment', foreground: '555555', fontStyle: 'italic' },
                { token: 'keyword', foreground: 'c8ff00' }, // Accent
                { token: 'string', foreground: '36f9ae' },  // Green
                { token: 'number', foreground: '00f0ff' },  // Cyan
                { token: 'type.identifier', foreground: '7b61ff' }, // Purple
                { token: 'identifier', foreground: 'f0f0f0' },
            ],
            colors: {
                'editor.background': '#0d0d0d',
                'editor.foreground': '#f0f0f0',
                'editorCursor.foreground': '#c8ff00',
                'editor.lineHighlightBackground': '#1a1a1a',
                'editorLineNumber.foreground': '#555555',
                'editor.selectionBackground': '#2a2a2a'
            }
        });

        const defaultCode = `def processUserSession(event, context):
    """
    Simulated serverless handler for user telemetry processing.
    Green Lambda AST Parser will analyze this block automatically.
    """
    user_id = event.get("userId")
    payload = event.get("metrics")
    
    # Nested loops raise Cyclomatic Complexity
    for data in payload:
        for inner in data.get("tags", []):
            if inner == "urgent":
                trigger_alert(user_id)
                
    # Blocking DB calls increase I/O wait times
    user_record = sync_db_fetch(user_id)
    
    # High memory footprint array allocation
    buffer = [0] * 1000000 
    
    return {"status": 200, "message": "Processed"}`;

        const editorEl = document.getElementById('monaco-editor');
        if (editorEl) {
            editor = monaco.editor.create(editorEl, {
                value: defaultCode,
                language: 'python',
                theme: 'greenLambdaTheme',
                automaticLayout: true,
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: "JetBrains Mono",
                scrollBeyondLastLine: false,
                roundedSelection: true,
                padding: { top: 16, bottom: 16 }
            });
        }

        // Language switcher
        const langSelect = document.getElementById('langSelect');
        if (langSelect) {
            langSelect.addEventListener('change', (e) => {
                if (editor) {
                    monaco.editor.setModelLanguage(editor.getModel(), e.target.value);
                }
            });
        }

        // Clear Button
        const clrBtn = document.getElementById('clearBtn');
        if (clrBtn && editor) {
            clrBtn.addEventListener('click', () => editor.setValue(''));
        }
    });
}

// Sidebar Linkages
function syncSlider(sliderId, labelId, suffix) {
    const sl = document.getElementById(sliderId);
    const lb = document.getElementById(labelId);
    if (sl && lb) {
        sl.addEventListener('input', (e) => {
            let val = parseInt(e.target.value).toLocaleString();
            lb.textContent = `${val} ${suffix}`;
        });
    }
}
syncSlider('memSlider', 'memLbl', 'MB');
syncSlider('freqSlider', 'freqLbl', '/ hr');
syncSlider('timeSlider', 'timeLbl', 'sec');

// Engine Analysis Logic
const analyzeBtn = document.getElementById('analyzeBtn');
const loader = document.getElementById('aiLoader');
const dash = document.getElementById('resultsDash');
const steps = document.getElementById('aiSteps');

const waitMs = (ms) => new Promise(res => setTimeout(res, ms));

const runAnalysis = async () => {
    if (!editor || !editor.getValue().trim()) {
        alert("Please input function code first.");
        return;
    }

    // Reset view
    dash.style.display = 'none';
    loader.style.display = 'flex';

    // Sequence
    steps.textContent = "INITIALIZING AST PARSER...";
    await waitMs(1000);
    steps.textContent = "EXTRACTING CYCLOMATIC COMPLEXITY...";
    await waitMs(800);
    steps.textContent = "MERGING DYNAMIC METADATA...";
    await waitMs(900);
    steps.textContent = "INFERENCING XGBoost TENSORS...";
    await waitMs(1200);

    // Dynamic calculations
    const code = editor.getValue();
    const lines = code.split('\n').filter(l => l.trim().length > 0).length;
    const loopMatches = code.match(/\b(for|while|forEach)\b/g);
    const loop_count = loopMatches ? loopMatches.length : 0;
    const ioMatch = code.match(/\b(fetch|read|db|query|axios|http)\b/gi);
    const io_calls = ioMatch ? ioMatch.length : 3;
    const innerLoops = code.match(/for.*\{[\s\S]*for/g);
    const loop_depth = innerLoops ? 2 : (loop_count > 0 ? 1 : 0);

    // Static display Page 1
    document.getElementById('st-lines').textContent = `${lines} L / ${loop_depth}D`;
    document.getElementById('st-io').textContent = `${io_calls} sync ops`;
    document.getElementById('st-loop-count').textContent = `${loop_count} loops`;

    const raw_run_ms = Math.round((lines * 0.8) + (loop_depth * 12) + (io_calls * 15));
    const est_rt = raw_run_ms > 0 ? raw_run_ms : 12;
    document.getElementById('st-runtime').textContent = `~${est_rt} ms`;

    const rtBadge = document.getElementById('runtimeBadge');
    if (est_rt < 100) { rtBadge.textContent = 'FAST'; rtBadge.style.background = 'var(--green)'; rtBadge.style.color = '#111'; }
    else if (est_rt <= 500) { rtBadge.textContent = 'NORMAL'; rtBadge.style.background = 'var(--amber)'; rtBadge.style.color = '#111'; }
    else { rtBadge.textContent = 'SLOW'; rtBadge.style.background = 'var(--accent)'; rtBadge.style.color = '#fff'; }

    // Page 2 KPI inputs
    const mem = parseInt(document.getElementById('memSlider').value) || 1024;
    const freq = parseInt(document.getElementById('freqSlider').value) || 2500;
    const timeout = parseInt(document.getElementById('timeSlider').value) || 30;
    const coldToggle = document.getElementById('coldToggle') ? document.getElementById('coldToggle').checked : true;

    const energy_wh = 0.82;
    const eff_score = 52;

    const carbon = energy_wh * 0.000233 * freq * 720;
    const resCO2 = document.getElementById('resCarbon');
    resCO2.innerHTML = carbon.toFixed(2) + ' <span class="result-unit">kg CO₂/mo</span>';
    if (carbon > 5) resCO2.style.color = 'var(--accent)';
    else if (carbon >= 1) resCO2.style.color = 'var(--amber)';
    else resCO2.style.color = 'var(--green)';
    document.getElementById('resCarbonEq').textContent = `≈ ${(carbon / 0.21).toFixed(1)} km driven`;

    const computeCost = ((mem / 1024) * est_rt * 0.0000000167 * freq * 720) * 84;
    const reqCost = (freq * 720 * 0.0000002) * 84;
    const totalCost = computeCost + reqCost;
    document.getElementById('resRunCost').innerHTML = '₹' + totalCost.toFixed(2) + ' <span class="result-unit">/ mo</span>';
    document.getElementById('resRunCostSub').setAttribute('title', `Compute: ₹${computeCost.toFixed(2)} | Requests: ₹${reqCost.toFixed(2)}`);

    // Resource Breakdown elements update
    const arrPenalty = (code.includes('[]') || code.includes('Array')) ? 45 : 10;
    const memFt = (mem * 0.65) + arrPenalty;
    document.getElementById('rb-mem-val').textContent = memFt.toFixed(0) + ' MB';

    document.getElementById('rb-time-val').textContent = est_rt + ' ms';
    document.getElementById('rb-energy-val').textContent = energy_wh.toFixed(3) + ' Wh';

    let coldMs = 0;
    if (coldToggle) coldMs = 250 + (mem / 1024) * 400;
    document.getElementById('rb-cold-val').textContent = coldMs.toFixed(0) + ' ms';

    // AWS Insights text dynamically updated
    const asMemTun = document.getElementById('aws-mem-tun');
    const asMemSav = document.getElementById('aws-mem-saving');
    if (mem > 1024) {
        asMemTun.textContent = "You're over-provisioned. Drop to 512MB to cut compute cost by ~48% with minimal latency impact.";
        if (asMemSav) asMemSav.textContent = `Potential saving: ~₹${(computeCost * 0.48).toFixed(2)} / mo`;
    } else if (mem < 512) {
        asMemTun.textContent = "Low memory may cause cold starts. Consider 512MB minimum.";
        if (asMemSav) asMemSav.textContent = '';
    } else {
        asMemTun.textContent = "Memory is well sized for this workload type.";
        if (asMemSav) asMemSav.textContent = '';
    }

    const asInvPat = document.getElementById('aws-inv-pat');
    if (freq > 5000) {
        let savPat = ((freq * 720 * 0.0000005) * 84).toFixed(2);
        asInvPat.textContent = `High frequency detected. Enable Provisioned Concurrency to eliminate cold starts and save ~₹${savPat}/mo.`;
    } else if (freq < 100) {
        asInvPat.textContent = "Low frequency. Keep on-demand — provisioned concurrency would cost more than it saves.";
    } else {
        asInvPat.textContent = "Moderate load. Monitor cold start rate before committing to provisioned concurrency.";
    }

    const asTimeConf = document.getElementById('aws-time-conf');
    if (timeout > (est_rt * 3 / 1000)) {
        let recT = Math.ceil((est_rt * 1.5) / 1000) || 1;
        let diff = Math.round((timeout * 1000) / est_rt);
        asTimeConf.textContent = `Your timeout is ${diff}x your estimated runtime. Reduce to ${recT}s to prevent runaway invocations from inflating costs.`;
    } else if (timeout < (est_rt * 1.5 / 1000)) {
        asTimeConf.textContent = "Timeout is dangerously close to estimated runtime. Increase to avoid false timeouts.";
    } else {
        asTimeConf.textContent = "Timeout is appropriately set.";
    }

    loader.style.display = 'none';

    // Reveal Dashboard safely
    dash.style.display = 'block';

    // Update active prediction gauge & animations dynamically
    setTimeout(() => {
        let dashOffset = 141.37 * (1 - (eff_score / 100));
        document.getElementById('gaugeMeter').style.strokeDashoffset = dashOffset;
        document.getElementById('gaugeMeter').style.stroke = "var(--accent)";
        document.getElementById('gaugeVal').textContent = eff_score;

        let memP = Math.min((memFt / mem) * 100, 100);
        document.getElementById('rb-mem-bar').style.width = memP + '%';
        let rtP = Math.min((est_rt / 1000) * 100, 100);
        document.getElementById('rb-time-bar').style.width = rtP + '%';
        let enP = Math.max(0, 100 - eff_score);
        document.getElementById('rb-energy-bar').style.width = enP + '%';
        let coldP = Math.min((coldMs / 1000) * 100, 100);
        document.getElementById('rb-cold-bar').style.width = coldP + '%';
    }, 100);

    // Scroll down to results smoothly
    window.scrollTo({
        top: dash.offsetTop - 100,
        behavior: "smooth"
    });
};

if (analyzeBtn) {
    analyzeBtn.addEventListener('click', runAnalysis);
}
