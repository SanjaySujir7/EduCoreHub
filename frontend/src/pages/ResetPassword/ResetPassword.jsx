import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiLockClosed } from 'react-icons/hi';
import Input from '../../components/Input/Input';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import Loader from '../../components/Loader/Loader';
import ThemeToggle from '../../components/ThemeToggle/ThemeToggle';
import { useToast } from '../../context/ToastContext';
import { resetPassword } from '../../services/authService';
import { pageVariants, pageTransition, fadeUp, staggerContainer } from '../../animations/pageTransition';
import styles from './ResetPassword.module.css';

const getStrength = (pw) => {
  let s = 0;
  if (pw.length >= 8) s++;
  if (/[A-Z]/.test(pw)) s++;
  if (/[0-9]/.test(pw)) s++;
  if (/[^A-Za-z0-9]/.test(pw)) s++;
  return s;
};

const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong'];
const strengthColors = ['#ef4444', '#f97316', '#eab308', '#22c55e'];

const ResetPassword = () => {
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { addToast } = useToast();
  const strength = useMemo(() => getStrength(password), [password]);

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    const e = {};
    if (password.length < 6) e.password = 'Min 6 characters';
    if (password !== confirm) e.confirm = 'Passwords do not match';
    setErrors(e);
    if (Object.keys(e).length) return;
    setLoading(true);
    try {
      const res = await resetPassword({ email: 'student@example.com', password });
      addToast(res.message, 'success');
    } catch {
      addToast('Reset failed', 'error');
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
            <div className={styles.icon}><HiLockClosed size={28} /></div>
            <h1 className={styles.title}>Reset Password</h1>
            <p className={styles.subtitle}>Create a new password</p>
          </motion.div>
          <motion.form onSubmit={handleSubmit} variants={fadeUp}>
            <Input label="Email" value="student@example.com" readOnly />
            <Input label="New Password" type="password" value={password} onChange={e => setPassword(e.target.value)} error={errors.password} />
            {password && (
              <div className={styles.strengthBar}>
                <div className={styles.strengthTrack}>
                  <motion.div className={styles.strengthFill} animate={{ width: `${(strength / 4) * 100}%`, backgroundColor: strengthColors[strength - 1] || '#ef4444' }} transition={{ duration: 0.4 }} />
                </div>
                <span className={styles.strengthLabel} style={{ color: strengthColors[strength - 1] }}>{strengthLabels[strength - 1] || 'Too short'}</span>
              </div>
            )}
            <Input label="Confirm Password" type="password" value={confirm} onChange={e => setConfirm(e.target.value)} error={errors.confirm} />
            <Button type="submit" fullWidth loading={loading}>Reset Password</Button>
          </motion.form>
          <motion.div className={styles.footer} variants={fadeUp}>
            <Link to="/" className={styles.link}>← Back to Login</Link>
          </motion.div>
        </motion.div>
      </Card>
    </motion.div>
  );
};

export default ResetPassword;
