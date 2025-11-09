import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

// Particle component for the trail effect
const Particle = ({ x, y, size, delay }) => {
  return (
    <motion.div
      className="absolute rounded-full bg-white"
      style={{
        width: size || 4,
        height: size || 4,
        x: x || 0,
        y: y || 0,
        position: "fixed",
        pointerEvents: "none",
        mixBlendMode: "screen",
        backgroundColor: "white",
        opacity: 0.8,
        filter: "blur(1px)",
        zIndex: 9998,
        transform: "translate(-50%, -50%)",
        willChange: "transform, opacity",
      }}
      initial={{ opacity: 0.8, scale: 1 }}
      animate={{
        opacity: 0,
        scale: 0.5,
        x: x,
        y: y,
        transition: {
          duration: 0.5,
          delay: delay || 0,
          ease: "easeOut",
        },
      }}
      exit={{ opacity: 0 }}
    />
  );
};

const CustomCursor = () => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [particles, setParticles] = useState([]);
  const cursorRef = useRef(null);
  const animationFrameRef = useRef();
  const lastMouseMoveRef = useRef({ x: 0, y: 0 });
  const targetPositionRef = useRef({ x: 0, y: 0 });
  const particleTimerRef = useRef(null);
  const lastParticleTimeRef = useRef(0);
  const velocityRef = useRef({ x: 0, y: 0 });
  const lastPositionRef = useRef({ x: 0, y: 0 });

  // Generate particles along the cursor's path
  const generateParticles = useCallback((x, y, velocity) => {
    const now = Date.now();
    if (now - lastParticleTimeRef.current > 16) {
      // ~60fps
      const speed = Math.sqrt(
        velocity.x * velocity.x + velocity.y * velocity.y
      );
      const particleCount = Math.min(Math.floor(speed / 2), 5);

      // Create particles with slight offset for trail effect
      const newParticles = Array(particleCount)
        .fill()
        .map((_, i) => {
          // Add some randomness to position for a more natural trail
          const offsetX = (Math.random() - 0.5) * 10;
          const offsetY = (Math.random() - 0.5) * 10;

          return {
            id: `${now}-${i}-${Math.random().toString(36).substr(2, 9)}`,
            x: x + offsetX,
            y: y + offsetY,
            size: Math.random() * 3 + 2, // Slightly smaller particles
            delay: i * 0.03, // Faster animation
          };
        });

      setParticles((prev) => {
        // Keep particles array from growing too large
        const updated = [...newParticles, ...prev];
        return updated.length > 25 ? updated.slice(0, 25) : updated;
      });

      lastParticleTimeRef.current = now;
    }
  }, []);

  // Handle mouse movement with requestAnimationFrame for smoother tracking
  const handleMouseMove = (e) => {
    const now = Date.now();
    const deltaTime = now - lastParticleTimeRef.current;

    // Calculate velocity for particle direction
    const newX = e.clientX;
    const newY = e.clientY;

    if (lastPositionRef.current.x !== 0 && lastPositionRef.current.y !== 0) {
      velocityRef.current = {
        x: (newX - lastPositionRef.current.x) * 2,
        y: (newY - lastPositionRef.current.y) * 2,
      };

      // Only generate particles when moving
      if (
        Math.abs(velocityRef.current.x) > 0.1 ||
        Math.abs(velocityRef.current.y) > 0.1
      ) {
        generateParticles(newX, newY, velocityRef.current);
      }
    }

    lastPositionRef.current = { x: newX, y: newY };
    targetPositionRef.current = { x: newX, y: newY };

    if (!animationFrameRef.current) {
      animationFrameRef.current = requestAnimationFrame(updateCursorPosition);
    }
  };

  const updateCursorPosition = () => {
    const { x: targetX, y: targetY } = targetPositionRef.current;
    const { x: lastX, y: lastY } = lastMouseMoveRef.current;

    // Directly follow the mouse with minimal smoothing
    const newX = lastX + (targetX - lastX) * 0.7; // Increased from 0.2 to 0.5 for more direct response
    const newY = lastY + (targetY - lastY) * 0.7;

    setPosition({ x: newX, y: newY });
    lastMouseMoveRef.current = { x: newX, y: newY };

    animationFrameRef.current = requestAnimationFrame(updateCursorPosition);
  };

  // Reset cursor position when window gets focus
  const handleWindowFocus = () => {
    // Force update cursor position when window regains focus
    const updateFromEvent = (e) => {
      if (e) {
        setPosition({ x: e.clientX, y: e.clientY });
        lastMouseMoveRef.current = { x: e.clientX, y: e.clientY };
        targetPositionRef.current = { x: e.clientX, y: e.clientY };
      }
      window.removeEventListener("mousemove", updateFromEvent);
    };

    // Add a one-time mousemove listener to get the latest position
    window.addEventListener("mousemove", updateFromEvent, { once: true });

    // Make sure cursor is visible
    setIsVisible(true);
  };

  useEffect(() => {
    // Hide default cursor
    document.body.style.cursor = "none";
    document.documentElement.style.cursor = "none";

    // Initial position update
    const handleInitialMove = (e) => {
      setPosition({ x: e.clientX, y: e.clientY });
      lastMouseMoveRef.current = { x: e.clientX, y: e.clientY };
      targetPositionRef.current = { x: e.clientX, y: e.clientY };
      window.removeEventListener("mousemove", handleInitialMove);
    };
    window.addEventListener("mousemove", handleInitialMove);

    // Handle hover states
    const handleMouseEnter = (e) => {
      if (
        e.target.matches('a, button, [role="button"], [data-cursor="hover"]')
      ) {
        setIsHovered(true);
      }
    };

    const handleMouseLeave = () => {
      setIsHovered(false);
    };

    // Handle visibility
    const handleMouseEnterDocument = () => {
      setIsVisible(true);
      // Reset position when re-entering the document
      const updateFromEvent = (e) => {
        setPosition({ x: e.clientX, y: e.clientY });
        lastMouseMoveRef.current = { x: e.clientX, y: e.clientY };
        targetPositionRef.current = { x: e.clientX, y: e.clientY };
        window.removeEventListener("mousemove", updateFromEvent);
      };
      window.addEventListener("mousemove", updateFromEvent, { once: true });
    };

    const handleMouseLeaveDocument = () => {
      // Keep cursor visible but update its position when returning
      setIsVisible(false);
    };

    // Add event listeners
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("focus", handleWindowFocus);
    window.addEventListener("pageshow", handleWindowFocus);
    document.addEventListener("mouseenter", handleMouseEnterDocument);
    document.addEventListener("mouseleave", handleMouseLeaveDocument);
    document.addEventListener("mouseover", handleMouseEnter);
    document.addEventListener("mouseout", handleMouseLeave);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameRef.current);
      if (particleTimerRef.current) {
        clearTimeout(particleTimerRef.current);
      }
      document.body.style.cursor = "";
      document.documentElement.style.cursor = "";
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("focus", handleWindowFocus);
      window.removeEventListener("pageshow", handleWindowFocus);
      document.removeEventListener("mouseenter", handleMouseEnterDocument);
      document.removeEventListener("mouseleave", handleMouseLeaveDocument);
      document.removeEventListener("mouseover", handleMouseEnter);
      document.removeEventListener("mouseout", handleMouseLeave);

      // Reset refs
      animationFrameRef.current = null;
      lastMouseMoveRef.current = { x: 0, y: 0 };
      targetPositionRef.current = { x: 0, y: 0 };
      lastPositionRef.current = { x: 0, y: 0 };
      velocityRef.current = { x: 0, y: 0 };
      setParticles([]);
    };
  }, []);

  // Glow effect style
  const glowStyle = {
    background:
      "radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 70%)",
    width: "150px",
    height: "150px",
    borderRadius: "50%",
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    pointerEvents: "none",
    zIndex: -1,
    opacity: 0.7,
    filter: "blur(60px)",
  };

  return (
    <>
      {/* Particle trail */}
      <AnimatePresence>
        {particles.map((particle) => {
          return (
            <Particle
              key={particle.id}
              x={particle.x}
              y={particle.y}
              size={particle.size}
              delay={particle.delay}
            />
          );
        })}
      </AnimatePresence>

      {/* Main cursor */}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            ref={cursorRef}
            className="fixed top-0 left-0 pointer-events-none z-9999"
            style={{
              transform: "translate(-50%, -50%)",
              willChange: "transform",
              mixBlendMode: "difference",
              x: position.x,
              y: position.y,
            }}
          >
            {/* Glow effect */}
            <div style={glowStyle} />

            {/* Outer circle */}
            <motion.div
              className="w-5 h-5 rounded-full border-2 border-white"
              style={{
                position: "relative",
                pointerEvents: "none",
                willChange: "transform",
                transform: isHovered ? "scale(1.5)" : "scale(1)",
                transition: "transform 0.1s ease-out",
              }}
            >
              {/* Inner dot */}
              <div
                className="absolute inset-0 m-auto w-1 h-1 bg-white rounded-full"
                style={{
                  boxShadow: "0 0 20px 5px rgba(255, 255, 255, 0.9)",
                  filter: "blur(1px)",
                  transform: isHovered ? "scale(0.5)" : "scale(1)",
                  transition: "transform 0.1s ease-out",
                }}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default CustomCursor;
