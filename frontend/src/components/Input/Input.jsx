import React, { useState } from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import styles from './Input.module.css';

const Input = ({ label, type = 'text', error, value, onChange, readOnly, ...props }) => {
  const [focused, setFocused] = useState(false);
  const active = focused || (value && value.length > 0);

  return (
    <div className={styles.wrapper}>
      <motion.input
        className={clsx(styles.input, error && styles.inputError, readOnly && styles.readOnly)}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        readOnly={readOnly}
        whileFocus={{ scale: 1.01 }}
        {...props}
      />
      <label className={clsx(styles.label, active && styles.labelActive)}>
        {label}
      </label>
      {error && <motion.span className={styles.error} initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }}>{error}</motion.span>}
    </div>
  );
};

export default Input;
