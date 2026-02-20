import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './Loader.module.css';

const Loader = ({ visible }) => (
  <AnimatePresence>
    {visible && (
      <motion.div
        className={styles.overlay}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <div className={styles.ring} />
      </motion.div>
    )}
  </AnimatePresence>
);

export default Loader;
