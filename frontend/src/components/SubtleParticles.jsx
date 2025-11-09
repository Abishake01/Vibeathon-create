import React, { useEffect, useRef } from "react";

/**
 * SubtleParticles - Twinkling starfield background
 * - No mouse interaction
 * - Lightweight twinkle animation
 * - Used globally from App.jsx
 */
export default function SubtleParticles() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const stars = [];
    const starCount = 150; // star density
    const targetFPS = 60;
    const frameInterval = 1000 / targetFPS;
    let lastFrameTime = 0;
    const startTime = performance.now();

    // Set canvas size
    const setCanvasSize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    setCanvasSize();
    window.addEventListener("resize", setCanvasSize);

    class Star {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.radius = Math.random() * 1.2 + 0.6; // small star sizes
        // Twinkle parameters
        this.baseOpacity = Math.random() * 0.4 + 0.4; // 0.4 - 0.8
        this.twinkleAmp = Math.random() * 0.35 + 0.15; // amplitude of twinkle
        this.phase = Math.random() * Math.PI * 2; // random phase so stars aren't in sync
      }

      update() {
        // No position or phase mutation needed; twinkle is time-based
      }

      draw(elapsedSeconds) {
        // Fixed 0.5s period => frequency = 2 Hz => omega = 4π rad/s
        const omega = Math.PI * 4;
        const opacity = Math.max(
          0,
          Math.min(
            1,
            this.baseOpacity +
              Math.sin(omega * elapsedSeconds + this.phase) * this.twinkleAmp
          )
        );

        // Simple star: a soft filled circle
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${opacity})`;
        ctx.fill();
      }
    }

    // Create stars
    for (let i = 0; i < starCount; i++) {
      stars.push(new Star());
    }

    // Animation loop
    const animate = (currentTime) => {
      const deltaTime = currentTime - lastFrameTime;
      if (deltaTime >= frameInterval) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const elapsedSeconds = (currentTime - startTime) / 3000;
        for (let i = 0; i < stars.length; i++) {
          stars[i].update();
          stars[i].draw(elapsedSeconds);
        }
        lastFrameTime = currentTime - (deltaTime % frameInterval);
      }
      requestAnimationFrame(animate);
    };

    animate(0);

    return () => {
      window.removeEventListener("resize", setCanvasSize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        zIndex: 1,
        pointerEvents: "none",
      }}
    />
  );
}
