import React from 'react';

interface ShimmerBadgeProps {
  children: React.ReactNode;
  className?: string;
}

export const ShimmerBadge: React.FC<ShimmerBadgeProps> = ({ children, className = '' }) => {
  return (
    <div className={`relative inline-flex items-center overflow-hidden rounded-full p-[1px] ${className}`}>
      {/* Rotating continuous gradient border beam */}
      <span className="absolute inset-[-1000%] animate-[spin_4s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#EAE7E0_0%,#171717_50%,#EAE7E0_100%)] opacity-30" />
      
      {/* Inner Badge Content */}
      <div className="relative inline-flex items-center gap-2 rounded-full bg-white px-4 py-1.5 text-xs font-semibold text-[#171717] backdrop-blur-md">
        {children}
      </div>
    </div>
  );
};
