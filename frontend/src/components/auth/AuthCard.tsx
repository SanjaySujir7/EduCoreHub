import React from "react";
import { motion } from "framer-motion";
import ThemeToggle from "./ThemeToggle";

interface AuthCardProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  variant?: "student" | "lecturer" | "admin";
}

const bgVariant = {
  student: "bg-liquid-glass",
  lecturer: "bg-liquid-glass",
  admin: "bg-liquid-admin",
};

const AuthCard: React.FC<AuthCardProps> = ({ children, title, subtitle, icon, variant = "student" }) => {
  return (
    <div className={`min-h-screen flex items-center justify-center p-4 ${bgVariant[variant]} transition-colors duration-500`}>
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md"
      >
        <div className="glass-card p-8 space-y-6">
          <div className="text-center space-y-2">
            {icon && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="flex justify-center mb-4"
              >
                {icon}
              </motion.div>
            )}
            <h1 className={`text-2xl font-bold ${variant === "admin" ? "text-gradient-admin" : "text-gradient-primary"}`}>
              {title}
            </h1>
            {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
          </div>
          {children}
        </div>
      </motion.div>
    </div>
  );
};

export default AuthCard;
