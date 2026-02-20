import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { cardVariants } from '../../animations/pageTransition';
import styles from './Card.module.css';

const Card = ({ children, className }) => (
  <motion.div
    className={clsx(styles.card, className)}
    variants={cardVariants}
    initial="initial"
    animate="animate"
  >
    {children}
  </motion.div>
);

export default Card;
