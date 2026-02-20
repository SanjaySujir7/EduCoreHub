import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import styles from './Button.module.css';

const Button = ({ children, onClick, loading, variant = 'primary', type = 'button', disabled, fullWidth }) => (
  <motion.button
    className={clsx(styles.button, styles[variant], fullWidth && styles.fullWidth, loading && styles.loading)}
    onClick={onClick}
    type={type}
    disabled={disabled || loading}
    whileTap={{ scale: 0.97 }}
    whileHover={{ scale: 1.025 }}
    transition={{ type: 'spring', stiffness: 400, damping: 20 }}
  >
    {loading ? <span className={styles.spinner} /> : children}
  </motion.button>
);

export default Button;
