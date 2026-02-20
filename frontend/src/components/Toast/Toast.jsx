import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from '../../context/ToastContext';
import { HiCheckCircle, HiXCircle, HiX } from 'react-icons/hi';
import styles from './Toast.module.css';

const Toast = () => {
  const { toasts, removeToast } = useToast();

  return (
    <div className={styles.container}>
      <AnimatePresence>
        {toasts.map(t => (
          <motion.div
            key={t.id}
            className={`${styles.toast} ${styles[t.type]}`}
            initial={{ opacity: 0, x: 80, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 80, scale: 0.9 }}
            transition={{ duration: 0.3 }}
          >
            {t.type === 'success' ? <HiCheckCircle size={20} /> : <HiXCircle size={20} />}
            <span>{t.message}</span>
            <button className={styles.close} onClick={() => removeToast(t.id)}>
              <HiX size={14} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default Toast;
