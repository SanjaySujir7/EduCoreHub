import React from "react";
import { motion } from "framer-motion";

const Loader: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-background">
    <motion.div className="flex gap-1.5">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-3 h-3 rounded-full bg-primary"
          animate={{ y: [0, -12, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
        />
      ))}
    </motion.div>
  </div>
);

export default Loader;
