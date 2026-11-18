import React from 'react';
import { motion } from 'framer-motion';

export const Footer: React.FC = () => {
  const socialLinks = [
    {
      name: 'Instagram',
      href: 'https://instagram.com',
      ariaLabel: 'Follow us on Instagram',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <rect width="20" height="20" x="2" y="2" rx="5" ry="5"/>
          <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
          <line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>
        </svg>
      ),
    },
    {
      name: 'Email',
      href: 'mailto:contact@nutz.fashion',
      ariaLabel: 'Send us an email',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <rect width="20" height="16" x="2" y="4" rx="2"/>
          <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
        </svg>
      ),
    },
    {
      name: 'WhatsApp',
      href: 'https://wa.me/',
      ariaLabel: 'Chat with us on WhatsApp',
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
          <path d="M16 15.5c-.3.3-.8.6-1.3.6-.5 0-1.8-.4-3.2-1.8-1.4-1.4-1.8-2.7-1.8-3.2 0-.5.3-1 .6-1.3l.8-.8c.2-.2.5-.2.7 0l1.2 1.2c.2.2.2.5 0 .7l-.5.5c.3.5.7.9 1.2 1.2l.5-.5c.2-.2.5-.2.7 0l1.2 1.2c.2.2.2.5 0 .7l-.8.8z" fill="currentColor" stroke="none" />
        </svg>
      ),
    },
  ];

  return (
    <footer className="bg-white border-t border-[#E8E8EF] py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-8 border-b border-[#E8E8EF]">
          {/* Brand & Tagline */}
          <div className="flex items-center">
            <div>
              <span className="font-extrabold text-[#171717] text-base tracking-tight font-sans">
                NUTZ <span className="text-[#171717]">FITTING ROOM</span>
              </span>
              <p className="text-xs text-slate-500">
                Bespoke Tailoring. Uncompromised Garment Drape.
              </p>
            </div>
          </div>

          {/* Links */}
          <div className="flex flex-wrap items-center gap-6 text-xs font-semibold text-slate-600">
            <a href="#tryon-workspace" className="hover:text-black transition-colors focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none rounded">
              Fitting Studio
            </a>
            <a href="#how-it-works" className="hover:text-black transition-colors focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none rounded">
              Craft &amp; Process
            </a>
            <a href="#features" className="hover:text-black transition-colors focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none rounded">
              Standards
            </a>
            <a href="#gallery" className="hover:text-black transition-colors focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none rounded">
              Lookbook
            </a>
          </div>
        </div>

        {/* Copyright & Circular Social Action Buttons */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-600 gap-6">
          <p>© {new Date().getFullYear()} NUTZ Fitting Room. All rights reserved.</p>

          {/* Circular Social & Contact Buttons (Instagram, Email, WhatsApp) */}
          <div className="flex items-center gap-3">
            {socialLinks.map((item) => (
              <motion.a
                key={item.name}
                href={item.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={item.ariaLabel}
                title={item.name}
                whileHover={{ y: -3, scale: 1.08 }}
                whileTap={{ scale: 0.92 }}
                className="w-11 h-11 rounded-full border border-[#171717]/15 bg-white text-[#171717] hover:bg-[#171717] hover:text-white hover:border-[#171717] flex items-center justify-center transition-colors duration-300 shadow-sm cursor-pointer"
              >
                {item.icon}
              </motion.a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};
