import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, X } from "lucide-react";

interface ToastNotificationProps {
  message: string;
  show: boolean;
  onClose: () => void;
}

const ToastNotification: React.FC<ToastNotificationProps> = ({ message, show, onClose }) => {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: -50, x: "-50%" }}
          animate={{ opacity: 1, y: 0, x: "-50%" }}
          exit={{ opacity: 0, y: -50, x: "-50%" }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          className="fixed top-6 left-1/2 z-[100] glass-card glow-success px-6 py-4 flex items-center gap-3 min-w-[300px]"
        >
          <CheckCircle className="text-primary shrink-0" size={20} />
          <span className="text-sm font-medium text-foreground flex-1">{message}</span>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
            <X size={16} />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ToastNotification;
