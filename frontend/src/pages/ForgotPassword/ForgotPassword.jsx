import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiKey } from 'react-icons/hi';
import Input from '../../components/Input/Input';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import Loader from '../../components/Loader/Loader';
import ThemeToggle from '../../components/ThemeToggle/ThemeToggle';
import { useToast } from '../../context/ToastContext';
import { forgotPassword } from '../../services/authService';
import { pageVariants, pageTransition, fadeUp, staggerContainer } from '../../animations/pageTransition';
import styles from './ForgotPassword.module.css';

const ForgotPassword = () => {
  const [usn, setUsn] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { addToast } = useToast();

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    if (!usn.trim()) { setError('USN is required'); return; }
    setError('');
    setLoading(true);
    try {
      await forgotPassword({ usn });
      addToast('Reset link sent to registered email', 'success');
    } catch {
      addToast('Failed to send reset link', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div className={styles.page} variants={pageVariants} initial="initial" animate="animate" exit="exit" transition={pageTransition}>
      <ThemeToggle />
      <Loader visible={loading} />
      <Card>
        <motion.div variants={staggerContainer} initial="initial" animate="animate">
          <motion.div className={styles.header} variants={fadeUp}>
            <div className={styles.icon}><HiKey size={28} /></div>
            <h1 className={styles.title}>Forgot Password</h1>
            <p className={styles.subtitle}>Enter your USN to receive a reset link</p>
          </motion.div>
          <motion.form onSubmit={handleSubmit} variants={fadeUp}>
            <Input label="USN" value={usn} onChange={e => setUsn(e.target.value)} error={error} />
            <Button type="submit" fullWidth loading={loading}>Send Reset Link</Button>
          </motion.form>
          <motion.div className={styles.footer} variants={fadeUp}>
            <Link to="/" className={styles.link}>← Back to Login</Link>
          </motion.div>
        </motion.div>
      </Card>
    </motion.div>
  );
};

export default ForgotPassword;
