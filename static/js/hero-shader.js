/**
 * hero-shader.js
 * Three.js WebGL shader background + smooth scramble animation
 * for MEMRACE landing hero section.
 */

(function () {
  'use strict';

  /* ════════════════════════════════════════════════════════════
     1. THREE.JS SHADER BACKGROUND
  ════════════════════════════════════════════════════════════ */

  const canvas = document.getElementById('hero-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  // Renderer — use lower pixel ratio for performance
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

  // Orthographic camera + full-screen quad
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const scene  = new THREE.Scene();
  const geo    = new THREE.PlaneGeometry(2, 2);

  /* ── GLSL Shaders ── */
  const vertexShader = /* glsl */`
    void main() {
      gl_Position = vec4(position, 1.0);
    }
  `;

  /*
   * Fragment shader: domain-warped FBM fluid field
   * Palette: near-black navy → deep electric blue → muted gold accent
   * Inspired by 21st.dev flowing gradient aesthetic.
   */
  const fragmentShader = /* glsl */`
    precision highp float;

    uniform float iTime;
    uniform vec2  iResolution;

    /* ── Hash & noise ── */
    float hash(vec2 p) {
      return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
    }

    float smoothNoise(vec2 p) {
      vec2 i = floor(p);
      vec2 f = fract(p);
      vec2 u = f * f * (3.0 - 2.0 * f);
      float a = hash(i);
      float b = hash(i + vec2(1.0, 0.0));
      float c = hash(i + vec2(0.0, 1.0));
      float d = hash(i + vec2(1.0, 1.0));
      return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
    }

    /* ── FBM (6 octaves) ── */
    float fbm(vec2 p) {
      float val = 0.0;
      float amp = 0.52;
      vec2  q   = p;
      for (int i = 0; i < 6; i++) {
        val += amp * smoothNoise(q);
        q    = q * 2.07 + vec2(1.71, 9.23);
        amp *= 0.47;
      }
      return val;
    }

    void main() {
      vec2 uv   = gl_FragCoord.xy / iResolution.xy;
      float asp = iResolution.x / iResolution.y;
      vec2 p    = (uv - 0.5) * vec2(asp, 1.0) * 2.0;

      /* Very slow time — premium feel, not flashy */
      float t = iTime * 0.07;

      /* ── Domain warping (3 layers) ── */
      vec2 q = vec2(
        fbm(p * 1.4 + t * 0.6),
        fbm(p * 1.4 + vec2(5.2, 1.3) + t * 0.5)
      );

      vec2 r = vec2(
        fbm(p * 1.1 + q * 1.1 + vec2(1.7, 9.2)  + t * 0.4),
        fbm(p * 1.1 + q * 1.1 + vec2(8.3, 2.8)  + t * 0.3)
      );

      float f = fbm(p * 0.9 + r * 0.85 + t * 0.2);
      f = f * 0.5 + 0.5;   /* remap to [0,1] */

      /* ── Color palette ── */
      vec3 ink      = vec3(0.018, 0.025, 0.065);   /* near-black navy */
      vec3 deepBlue = vec3(0.030, 0.095, 0.380);   /* deep electric blue */
      vec3 midBlue  = vec3(0.060, 0.170, 0.560);   /* rich blue */
      vec3 cyanTint = vec3(0.040, 0.280, 0.480);   /* subtle teal */
      vec3 warmGold = vec3(0.520, 0.330, 0.055);   /* warm gold accent */

      vec3 col = ink;
      col = mix(col, deepBlue, smoothstep(0.18, 0.58, f) * 0.85);
      col = mix(col, midBlue,  smoothstep(0.40, 0.72, f + q.x * 0.22) * 0.50);
      col = mix(col, cyanTint, smoothstep(0.50, 0.78, r.y + 0.1) * 0.22);
      col = mix(col, warmGold, smoothstep(0.68, 0.92, f * (q.x + 0.5)) * 0.09);

      /* ── Top-center glow bloom (electric blue) ── */
      vec2 bloom  = uv - vec2(0.5, 0.22);
      float bDist = dot(bloom, bloom * vec2(1.0, 0.6));
      col += vec3(0.04, 0.10, 0.38) * exp(-bDist * 7.5) * 0.55;

      /* ── Radial vignette (darkens edges) ── */
      vec2 vc       = uv - 0.5;
      float vignette = 1.0 - dot(vc, vc) * 2.8;
      col *= clamp(vignette, 0.0, 1.0);

      /* ── Subtle gamma lift ── */
      col = pow(max(col, 0.0), vec3(0.88));

      gl_FragColor = vec4(col, 1.0);
    }
  `;

  /* ── Shader material + mesh ── */
  const uniforms = {
    iTime:       { value: 0.0 },
    iResolution: { value: new THREE.Vector2() },
  };

  const mat  = new THREE.ShaderMaterial({ uniforms, vertexShader, fragmentShader });
  const mesh = new THREE.Mesh(geo, mat);
  scene.add(mesh);

  /* ── Resize ── */
  function resize() {
    const w = canvas.parentElement.offsetWidth  || window.innerWidth;
    const h = canvas.parentElement.offsetHeight || window.innerHeight;
    renderer.setSize(w, h, false);
    uniforms.iResolution.value.set(w, h);
  }
  resize();
  window.addEventListener('resize', resize, { passive: true });

  /* ── Render loop ── */
  const clock = new THREE.Clock();
  (function animate() {
    requestAnimationFrame(animate);
    uniforms.iTime.value = clock.getElapsedTime();
    renderer.render(scene, camera);
  })();


  /* ════════════════════════════════════════════════════════════
     2. SCRAMBLE TEXT ANIMATION
     Time-based (not frame-based) → consistent speed regardless of fps.
     Eased progress → starts instant, slows to a smooth settle.
  ════════════════════════════════════════════════════════════ */

  const PHRASES = [
    'AI-Powered Flashcards',
    'Smart Learning System',
    'Memrace Intelligence',
  ];

  /* Character pool — readable, not symbol-heavy */
  const POOL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

  const SCRAMBLE_MS = 2000;   /* duration of scramble effect (ms) */
  const PAUSE_MS    = 3200;   /* how long settled text stays visible (ms) */

  let el          = document.getElementById('scramble-text');
  let phraseIdx   = 0;
  let rafId       = null;

  function scrambleFrame(target, elapsed) {
    /* Cubic ease-out: fast start, smooth settle */
    const raw      = Math.min(elapsed / SCRAMBLE_MS, 1);
    const eased    = 1 - Math.pow(1 - raw, 3);
    const revealed = Math.floor(eased * target.length);

    el.textContent = target
      .split('')
      .map((ch, i) => {
        if (ch === ' ') return ' ';
        if (i < revealed) return ch;
        return POOL[Math.floor(Math.random() * POOL.length)];
      })
      .join('');
  }

  function runScramble(target, onComplete) {
    if (!el) return;
    cancelAnimationFrame(rafId);
    const start = performance.now();

    function tick(now) {
      const elapsed = now - start;
      scrambleFrame(target, elapsed);
      if (elapsed < SCRAMBLE_MS) {
        rafId = requestAnimationFrame(tick);
      } else {
        el.textContent = target;       /* snap to final text */
        if (onComplete) onComplete();
      }
    }
    rafId = requestAnimationFrame(tick);
  }

  function scheduleNext() {
    setTimeout(() => {
      phraseIdx = (phraseIdx + 1) % PHRASES.length;
      runScramble(PHRASES[phraseIdx], scheduleNext);
    }, PAUSE_MS);
  }

  /* Kick off: show phrase 0 first, then cycle */
  if (el) {
    runScramble(PHRASES[0], scheduleNext);
  }

})();
