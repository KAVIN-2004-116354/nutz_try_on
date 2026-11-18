import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export const RadiantGrid: React.FC = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: e.clientX,
        y: e.clientY,
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
      {/* Subtle Fine Dot Matrix Grid */}
      <div 
        className="absolute inset-0 opacity-[0.45]"
        style={{
          backgroundImage: `radial-gradient(circle at center, rgba(23, 23, 23, 0.12) 1px, transparent 1px)`,
          backgroundSize: '28px 28px',
          maskImage: 'radial-gradient(ellipse 80% 60% at 50% 30%, black 40%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 80% 60% at 50% 30%, black 40%, transparent 100%)',
        }}
      />

      {/* Floating Animated Luminous Orbs */}
      <motion.div
        animate={{
          scale: [1, 1.15, 1],
          opacity: [0.35, 0.55, 0.35],
          x: [0, 20, 0],
          y: [0, -15, 0],
        }}
        transition={{
          duration: 9,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute -top-32 left-1/2 -translate-x-1/2 w-[650px] h-[350px] bg-gradient-to-b from-[#F2EFE8] via-[#EAE4D6]/50 to-transparent rounded-full blur-3xl"
      />

      <motion.div
        animate={{
          scale: [1.1, 1, 1.1],
          opacity: [0.2, 0.4, 0.2],
          x: [0, -25, 0],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute top-48 left-1/4 w-[450px] h-[300px] bg-gradient-to-tr from-[#EFEAE1]/60 to-transparent rounded-full blur-3xl"
      />

      {/* Interactive Cursor Spotlight Glow */}
      <div
        className="absolute w-[400px] h-[400px] rounded-full pointer-events-none transition-transform duration-300 ease-out blur-3xl opacity-20"
        style={{
          background: 'radial-gradient(circle, rgba(23, 23, 23, 0.08) 0%, transparent 70%)',
          left: mousePosition.x - 200,
          top: mousePosition.y - 200,
        }}
      />
    </div>
  );
};
