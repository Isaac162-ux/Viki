// ViKi Holographic Core - Three.js Orb Component
// A central 3D orb representing ViKi's state with particle effects and animations

import { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';

interface ViKiOrbProps {
  /** Current state of ViKi */
  state: 'idle' | 'listening' | 'thinking' | 'speaking' | 'executing' | 'awaiting_confirmation' | 'error' | 'disconnected';
  /** Container width */
  width?: number;
  /** Container height */
  height?: number;
  /** Whether to enable mouse interaction */
  interactive?: boolean;
  /** Custom className */
  className?: string;
  /** Callback when state animation completes */
  onStateChange?: (state: string) => void;
}

interface OrbColors {
  primary: THREE.Color;
  secondary: THREE.Color;
  accent: THREE.Color;
  background: THREE.Color;
  particles: THREE.Color[];
}

// State-specific color configurations
const STATE_COLORS: Record<ViKiOrbProps['state'], OrbColors> = {
  idle: {
    primary: new THREE.Color(0x00d4ff),      // Cyan
    secondary: new THREE.Color(0x0066cc),    // Blue
    accent: new THREE.Color(0xff00ff),       // Magenta
    background: new THREE.Color(0x020817),   // Deep navy
    particles: [
      new THREE.Color(0x00d4ff),
      new THREE.Color(0x00ffff),
      new THREE.Color(0x8844ff),
    ],
  },
  listening: {
    primary: new THREE.Color(0x00ff88),      // Green-cyan
    secondary: new THREE.Color(0x00cc66),
    accent: new THREE.Color(0x88ff00),
    background: new THREE.Color(0x021708),
    particles: [
      new THREE.Color(0x00ff88),
      new THREE.Color(0x00ffcc),
      new THREE.Color(0x88ff88),
    ],
  },
  thinking: {
    primary: new THREE.Color(0xffaa00),      // Amber
    secondary: new THREE.Color(0xcc8800),
    accent: new THREE.Color(0xffdd00),
    background: new THREE.Color(0x171002),
    particles: [
      new THREE.Color(0xffaa00),
      new THREE.Color(0xffcc44),
      new THREE.Color(0xff8800),
    ],
  },
  speaking: {
    primary: new THREE.Color(0xff4488),      // Pink-red
    secondary: new THREE.Color(0xcc3366),
    accent: new THREE.Color(0xff00aa),
    background: new THREE.Color(0x170208),
    particles: [
      new THREE.Color(0xff4488),
      new THREE.Color(0xff88cc),
      new THREE.Color(0xff0088),
    ],
  },
  executing: {
    primary: new THREE.Color(0x4488ff),      // Blue
    secondary: new THREE.Color(0x3366cc),
    accent: new THREE.Color(0x0088ff),
    background: new THREE.Color(0x020817),
    particles: [
      new THREE.Color(0x4488ff),
      new THREE.Color(0x88aaff),
      new THREE.Color(0x0066ff),
    ],
  },
  awaiting_confirmation: {
    primary: new THREE.Color(0xff8800),      // Orange
    secondary: new THREE.Color(0xcc6600),
    accent: new THREE.Color(0xffaa00),
    background: new THREE.Color(0x170f02),
    particles: [
      new THREE.Color(0xff8800),
      new THREE.Color(0xffaa44),
      new THREE.Color(0xff6600),
    ],
  },
  error: {
    primary: new THREE.Color(0xff2244),      // Red
    secondary: new THREE.Color(0xcc1133),
    accent: new THREE.Color(0xff0033),
    background: new THREE.Color(0x170204),
    particles: [
      new THREE.Color(0xff2244),
      new THREE.Color(0xff6688),
      new THREE.Color(0xcc0022),
    ],
  },
  disconnected: {
    primary: new THREE.Color(0x555555),      // Gray
    secondary: new THREE.Color(0x333333),
    accent: new THREE.Color(0x777777),
    background: new THREE.Color(0x0a0a0a),
    particles: [
      new THREE.Color(0x555555),
      new THREE.Color(0x777777),
      new THREE.Color(0x999999),
    ],
  },
};

// Animation configurations per state
const STATE_ANIMATIONS = {
  idle: {
    rotationSpeed: 0.0005,
    pulseSpeed: 0.5,
    pulseIntensity: 0.15,
    particleSpeed: 0.2,
    particleCount: 800,
    ringRotation: 0.001,
    distortion: 0.02,
  },
  listening: {
    rotationSpeed: 0.001,
    pulseSpeed: 2.0,
    pulseIntensity: 0.3,
    particleSpeed: 0.5,
    particleCount: 1200,
    ringRotation: 0.003,
    distortion: 0.05,
  },
  thinking: {
    rotationSpeed: 0.002,
    pulseSpeed: 1.0,
    pulseIntensity: 0.25,
    particleSpeed: 0.8,
    particleCount: 1000,
    ringRotation: 0.002,
    distortion: 0.08,
  },
  speaking: {
    rotationSpeed: 0.0015,
    pulseSpeed: 3.0,
    pulseIntensity: 0.4,
    particleSpeed: 1.0,
    particleCount: 1500,
    ringRotation: 0.004,
    distortion: 0.1,
  },
  executing: {
    rotationSpeed: 0.003,
    pulseSpeed: 1.5,
    pulseIntensity: 0.2,
    particleSpeed: 0.6,
    particleCount: 900,
    ringRotation: 0.005,
    distortion: 0.06,
  },
  awaiting_confirmation: {
    rotationSpeed: 0.001,
    pulseSpeed: 1.2,
    pulseIntensity: 0.35,
    particleSpeed: 0.4,
    particleCount: 1100,
    ringRotation: 0.002,
    distortion: 0.04,
  },
  error: {
    rotationSpeed: 0.0005,
    pulseSpeed: 2.5,
    pulseIntensity: 0.5,
    particleSpeed: 1.2,
    particleCount: 600,
    ringRotation: -0.001,
    distortion: 0.15,
  },
  disconnected: {
    rotationSpeed: 0.0002,
    pulseSpeed: 0.3,
    pulseIntensity: 0.05,
    particleSpeed: 0.1,
    particleCount: 200,
    ringRotation: 0,
    distortion: 0,
  },
};

export function ViKiOrb({
  state = 'idle',
  width = 400,
  height = 400,
  interactive = true,
  className = '',
  onStateChange,
}: ViKiOrbProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isReady, setIsReady] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

  // Three.js objects
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const coreRef = useRef<THREE.Mesh | null>(null);
  const particlesRef = useRef<THREE.Points | null>(null);
  const ringRef = useRef<THREE.Mesh | null>(null);
  const glowRef = useRef<THREE.Mesh | null>(null);
  const animationIdRef = useRef<number>(0);
  const currentStateRef = useRef(state);
  const targetColorsRef = useRef(STATE_COLORS[state]);
  const currentAnimConfigRef = useRef(STATE_ANIMATIONS[state]);
  const timeRef = useRef(0);
  const mouseRef = useRef({ x: 0, y: 0 });

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mediaQuery.matches);
    const handler = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current || !canvasRef.current) return;

    const container = containerRef.current;
    const canvas = canvasRef.current;

    // Scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // Camera
    const aspect = width / height;
    const camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
    camera.position.z = 5;
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    rendererRef.current = renderer;

    // ---- Core Sphere (Main Orb) ----
    const coreGeometry = new THREE.SphereGeometry(1.2, 64, 64);
    const coreMaterial = new THREE.MeshPhysicalMaterial({
      color: targetColorsRef.current.primary,
      metalness: 0.3,
      roughness: 0.1,
      transmission: 0.8,
      thickness: 0.5,
      ior: 1.33,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      side: THREE.DoubleSide,
    });
    const core = new THREE.Mesh(coreGeometry, coreMaterial);
    coreRef.current = core;
    scene.add(core);

    // ---- Inner Core (Darker center) ----
    const innerGeometry = new THREE.SphereGeometry(0.4, 32, 32);
    const innerMaterial = new THREE.MeshBasicMaterial({
      color: targetColorsRef.current.background,
      transparent: true,
      opacity: 0.9,
    });
    const innerCore = new THREE.Mesh(innerGeometry, innerMaterial);
    core.add(innerCore);

    // ---- Accretion Ring ----
    const ringGeometry = new THREE.RingGeometry(1.5, 2.2, 64);
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: targetColorsRef.current.accent,
      transparent: true,
      opacity: 0.4,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
    });
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.rotation.x = -Math.PI / 2;
    ringRef.current = ring;
    scene.add(ring);

    // ---- Glow/Halo ----
    const glowGeometry = new THREE.SphereGeometry(1.8, 32, 32);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: targetColorsRef.current.primary,
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
    glowRef.current = glow;
    scene.add(glow);

    // ---- Particle System ----
    const particleCount = currentAnimConfigRef.current.particleCount;
    const particleGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    const colors = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);
    const phases = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      const radius = 1.2 + Math.random() * 1.5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);

      sizes[i] = Math.random() * 2 + 0.5;

      const color = targetColorsRef.current.particles[
        Math.floor(Math.random() * targetColorsRef.current.particles.length)
      ];
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;

      // Random orbital velocity
      velocities[i * 3] = (Math.random() - 0.5) * 0.01;
      velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.01;
      velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.01;

      phases[i] = Math.random() * Math.PI * 2;
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    particleGeometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    particleGeometry.setAttribute('phase', new THREE.BufferAttribute(phases, 1));

    const particleMaterial = new THREE.PointsMaterial({
      size: 0.04,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });

    const particles = new THREE.Points(particleGeometry, particleMaterial);
    particlesRef.current = particles;
    scene.add(particles);

    // ---- Filaments (Connecting lines) ----
    const filamentGeometry = new THREE.BufferGeometry();
    const filamentCount = 50;
    const filamentPositions = new Float32Array(filamentCount * 2 * 3);
    const filamentColors = new Float32Array(filamentCount * 2 * 3);

    for (let i = 0; i < filamentCount; i++) {
      const startRadius = 1.2;
      const endRadius = 2.5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      const sx = startRadius * Math.sin(phi) * Math.cos(theta);
      const sy = startRadius * Math.sin(phi) * Math.sin(theta);
      const sz = startRadius * Math.cos(phi);

      const ex = endRadius * Math.sin(phi) * Math.cos(theta);
      const ey = endRadius * Math.sin(phi) * Math.sin(theta);
      const ez = endRadius * Math.cos(phi);

      filamentPositions[i * 6] = sx;
      filamentPositions[i * 6 + 1] = sy;
      filamentPositions[i * 6 + 2] = sz;
      filamentPositions[i * 6 + 3] = ex;
      filamentPositions[i * 6 + 4] = ey;
      filamentPositions[i * 6 + 5] = ez;

      const color = targetColorsRef.current.particles[
        Math.floor(Math.random() * targetColorsRef.current.particles.length)
      ];
      filamentColors[i * 6] = color.r;
      filamentColors[i * 6 + 1] = color.g;
      filamentColors[i * 6 + 2] = color.b;
      filamentColors[i * 6 + 3] = color.r * 0.3;
      filamentColors[i * 6 + 4] = color.g * 0.3;
      filamentColors[i * 6 + 5] = color.b * 0.3;
    }

    filamentGeometry.setAttribute('position', new THREE.BufferAttribute(filamentPositions, 3));
    filamentGeometry.setAttribute('color', new THREE.BufferAttribute(filamentColors, 3));

    const filamentMaterial = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.3,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    const filaments = new THREE.LineSegments(filamentGeometry, filamentMaterial);
    scene.add(filaments);

    // ---- Lights ----
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(targetColorsRef.current.primary, 1, 10);
    pointLight.position.set(0, 0, 3);
    scene.add(pointLight);

    const pointLight2 = new THREE.PointLight(targetColorsRef.current.accent, 0.5, 10);
    pointLight2.position.set(3, 3, -2);
    scene.add(pointLight2);

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current || !cameraRef.current || !rendererRef.current) return;
      const w = containerRef.current.clientWidth || width;
      const h = containerRef.current.clientHeight || height;
      cameraRef.current.aspect = w / h;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    // Mouse interaction
    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    };

    container.addEventListener('mousemove', handleMouseMove);

    // Animation loop
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);
      timeRef.current += 1 / 60;

      if (!sceneRef.current || !cameraRef.current || !rendererRef.current) return;

      const animConfig = currentAnimConfigRef.current;
      const colors = targetColorsRef.current;

      // Rotate core
      if (coreRef.current) {
        coreRef.current.rotation.y += animConfig.rotationSpeed * (reducedMotion ? 0.1 : 1);
        coreRef.current.rotation.x += animConfig.rotationSpeed * 0.5 * (reducedMotion ? 0.1 : 1);

        // Pulse animation
        const pulse = Math.sin(timeRef.current * animConfig.pulseSpeed) * animConfig.pulseIntensity + 1;
        coreRef.current.scale.setScalar(pulse);

        // Update material color smoothly
        const material = coreRef.current.material as THREE.MeshPhysicalMaterial;
        material.color.lerp(colors.primary, 0.05);
        material.emissive = colors.primary.clone().multiplyScalar(0.1);
      }

      // Rotate ring
      if (ringRef.current) {
        ringRef.current.rotation.z += animConfig.ringRotation * (reducedMotion ? 0.1 : 1);
        const ringMat = ringRef.current.material as THREE.MeshBasicMaterial;
        ringMat.color.lerp(colors.accent, 0.05);
        ringMat.opacity = 0.3 + Math.sin(timeRef.current * animConfig.pulseSpeed * 2) * 0.1;
      }

      // Pulse glow
      if (glowRef.current) {
        const glowScale = 1 + Math.sin(timeRef.current * animConfig.pulseSpeed) * 0.1;
        glowRef.current.scale.setScalar(glowScale);
        const glowMat = glowRef.current.material as THREE.MeshBasicMaterial;
        glowMat.color.lerp(colors.primary, 0.05);
        glowMat.opacity = 0.05 + Math.sin(timeRef.current * animConfig.pulseSpeed) * 0.05;
      }

      // Animate particles
      if (particlesRef.current) {
        const positions = particlesRef.current.geometry.attributes.position.array as Float32Array;
        const velocities = particlesRef.current.geometry.attributes.velocity.array as Float32Array;
        const phases = particlesRef.current.geometry.attributes.phase.array as Float32Array;
        const particleMaterial = particlesRef.current.material as THREE.PointsMaterial;

        for (let i = 0; i < particleCount; i++) {
          const speed = animConfig.particleSpeed * (reducedMotion ? 0.1 : 1);

          // Orbital motion
          positions[i * 3] += velocities[i * 3] * speed;
          positions[i * 3 + 1] += velocities[i * 3 + 1] * speed;
          positions[i * 3 + 2] += velocities[i * 3 + 2] * speed;

          // Add some noise
          positions[i * 3] += Math.sin(timeRef.current * 2 + phases[i]) * 0.001;
          positions[i * 3 + 1] += Math.cos(timeRef.current * 2 + phases[i]) * 0.001;

          // Keep particles in orbital range
          const dist = Math.sqrt(
            positions[i * 3] ** 2 + positions[i * 3 + 1] ** 2 + positions[i * 3 + 2] ** 2
          );
          if (dist > 3 || dist < 1) {
            // Reset to random orbital position
            const radius = 1.2 + Math.random() * 1.5;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
            positions[i * 3 + 2] = radius * Math.cos(phi);
          }
        }
        particlesRef.current.geometry.attributes.position.needsUpdate = true;

        // Pulse particle sizes
        particleMaterial.size = 0.04 + Math.sin(timeRef.current * animConfig.pulseSpeed) * 0.01;
        particleMaterial.color.lerp(colors.primary, 0.02);
      }

      // Animate filaments
      if (filaments && filamentGeometry.attributes.position) {
        // Subtle filament animation handled via shader in production
      }

      // Mouse interaction - subtle camera drift
      if (interactive && cameraRef.current) {
        cameraRef.current.position.x += (mouseRef.current.x * 0.3 - cameraRef.current.position.x) * 0.02;
        cameraRef.current.position.y += (mouseRef.current.y * 0.3 - cameraRef.current.position.y) * 0.02;
        cameraRef.current.lookAt(0, 0, 0);
      }

      rendererRef.current.render(scene, cameraRef.current);
    };

    animate();
    setIsReady(true);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationIdRef.current);
      window.removeEventListener('resize', handleResize);
      container.removeEventListener('mousemove', handleMouseMove);

      // Dispose Three.js objects
      coreGeometry.dispose();
      coreMaterial.dispose();
      innerGeometry.dispose();
      innerMaterial.dispose();
      ringGeometry.dispose();
      ringMaterial.dispose();
      glowGeometry.dispose();
      glowMaterial.dispose();
      particleGeometry.dispose();
      particleMaterial.dispose();
      filamentGeometry.dispose();
      filamentMaterial.dispose();
      ambientLight.dispose();
      pointLight.dispose();
      pointLight2.dispose();
      rendererRef.current?.dispose();
    };
  }, [width, height, interactive, reducedMotion]);

  // Handle state changes with smooth transitions
  useEffect(() => {
    if (currentStateRef.current === state) return;
    currentStateRef.current = state;

    // Smoothly transition to new state colors and animation config
    targetColorsRef.current = STATE_COLORS[state];
    currentAnimConfigRef.current = STATE_ANIMATIONS[state];

    // Update particle count if needed
    if (particlesRef.current) {
      const newCount = currentAnimConfigRef.current.particleCount;
      // In production, you'd recreate the particle system with new count
      // For now, we just adjust opacity of excess particles
    }

    onStateChange?.(state);
  }, [state, onStateChange]);

  // State indicator labels
  const stateLabels: Record<ViKiOrbProps['state'], string> = {
    idle: 'Ready',
    listening: 'Listening...',
    thinking: 'Thinking...',
    speaking: 'Speaking...',
    executing: 'Executing...',
    awaiting_confirmation: 'Awaiting Confirmation',
    error: 'Error',
    disconnected: 'Disconnected',
  };

  if (!isReady) {
    return (
      <div
        ref={containerRef}
        className={`viki-orb-container ${className}`}
        style={{
          width,
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'transparent',
        }}
      >
        <div className="viki-orb-loading" style={{ color: '#00d4ff', fontFamily: 'monospace' }}>
          Initializing ViKi Core...
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`viki-orb-container ${className}`}
      style={{
        width,
        height,
        position: 'relative',
        background: 'transparent',
      }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
          borderRadius: '50%',
        }}
        aria-label={`ViKi status: ${stateLabels[state]}`}
        role="img"
      />
      <div
        className="viki-orb-state-label"
        style={{
          position: 'absolute',
          bottom: -30,
          left: '50%',
          transform: 'translateX(-50%)',
          color: STATE_COLORS[state].primary.getStyle(),
          fontFamily: 'var(--font-mono, monospace)',
          fontSize: '12px',
          fontWeight: 500,
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
          textShadow: `0 0 10px ${STATE_COLORS[state].primary.getStyle()}`,
          transition: 'all 0.3s ease',
        }}
      >
        {stateLabels[state]}
      </div>
      <style jsx>{`
        .viki-orb-container {
          position: relative;
        }
        .viki-orb-loading {
          animation: pulse 1.5s ease-in-out infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
        .viki-orb-state-label {
          pointer-events: none;
          user-select: none;
        }
      `}</style>
    </div>
  );
}

// Hook for controlling ViKi Orb from parent components
export function useViKiOrb() {
  const [state, setState] = useState<ViKiOrbProps['state']>('idle');

  const setOrbState = useCallback((newState: ViKiOrbProps['state']) => {
    setState(newState);
  }, []);

  return { state, setOrbState };
}

export default ViKiOrb;