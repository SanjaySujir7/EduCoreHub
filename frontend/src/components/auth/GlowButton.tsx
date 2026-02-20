import React from "react";
import { motion } from "framer-motion";

interface GlowButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "accent" | "admin" | "success";
  loading?: boolean;
  disabled?: boolean;
  type?: "button" | "submit";
  className?: string;
}

const glowMap = {
  primary: "glow-primary bg-primary text-primary-foreground hover:brightness-110",
  accent: "glow-accent bg-accent text-accent-foreground hover:brightness-110",
  admin: "glow-admin bg-destructive text-destructive-foreground hover:brightness-110",
  success: "glow-success bg-primary text-primary-foreground hover:brightness-110",
};

const GlowButton: React.FC<GlowButtonProps> = ({
  children, onClick, variant = "primary", loading, disabled, type = "button", className = "",
}) => {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
      className={`relative w-full py-3 px-6 rounded-xl font-semibold text-sm tracking-wide
        transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed
        ${glowMap[variant]} ${className}`}
    >
      {loading ? (
        <div className="flex items-center justify-center gap-2">
          <motion.div
            className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
          />
          <span>Processing...</span>
        </div>
      ) : (
        children
      )}
    </motion.button>
  );
};

export default GlowButton;
