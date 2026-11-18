import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface WordCycleProps {
  words: string[];
  intervalMs?: number;
  className?: string;
}

export const WordCycle: React.FC<WordCycleProps> = ({
  words,
  intervalMs = 3000,
  className = '',
}) => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % words.length);
    }, intervalMs);
    return () => clearInterval(timer);
  }, [words.length, intervalMs]);

  return (
    <span className={`inline-block relative overflow-hidden align-top text-left ${className}`}>
      <AnimatePresence mode="wait">
        <motion.span
          key={words[index]}
          initial={{ y: 28, opacity: 0, filter: 'blur(6px)' }}
          animate={{ y: 0, opacity: 1, filter: 'blur(0px)' }}
          exit={{ y: -28, opacity: 0, filter: 'blur(6px)' }}
          transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
          className="inline-block"
        >
          {words[index]}
        </motion.span>
      </AnimatePresence>
    </span>
  );
};
