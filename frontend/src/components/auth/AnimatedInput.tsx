import React, { useState } from "react";
import { motion } from "framer-motion";

interface AnimatedInputProps {
  label: string;
  type?: string;
  value: string;
  onChange: (val: string) => void;
  readOnly?: boolean;
  error?: string;
}

const AnimatedInput: React.FC<AnimatedInputProps> = ({ label, type = "text", value, onChange, readOnly, error }) => {
  const [focused, setFocused] = useState(false);
  const isActive = focused || value.length > 0;

  return (
    <motion.div
      className="relative w-full"
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <input
        type={type}
        value={value}
        readOnly={readOnly}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        className={`peer w-full px-4 pt-6 pb-2 rounded-xl bg-secondary/50 border text-foreground 
          outline-none transition-all duration-300 font-sans text-sm
          ${focused ? "border-primary glow-primary" : "border-border"}
          ${error ? "border-destructive" : ""}
          ${readOnly ? "opacity-60 cursor-not-allowed" : ""}
          placeholder-transparent`}
        placeholder={label}
      />
      <label
        className={`absolute left-4 transition-all duration-300 pointer-events-none font-medium
          ${isActive ? "top-1.5 text-[10px] text-primary" : "top-4 text-sm text-muted-foreground"}`}
      >
        {label}
      </label>
      {focused && (
        <motion.div
          className="absolute bottom-0 left-1/2 h-[2px] bg-primary rounded-full"
          initial={{ width: 0, x: "-50%" }}
          animate={{ width: "90%", x: "-50%" }}
          transition={{ duration: 0.3 }}
        />
      )}
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-destructive text-xs mt-1 ml-1"
        >
          {error}
        </motion.p>
      )}
    </motion.div>
  );
};

export default AnimatedInput;
