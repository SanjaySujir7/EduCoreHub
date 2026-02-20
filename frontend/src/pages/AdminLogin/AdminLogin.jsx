import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiShieldCheck } from 'react-icons/hi';
import Input from '../../components/Input/Input';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import Loader from '../../components/Loader/Loader';
import ThemeToggle from '../../components/ThemeToggle/ThemeToggle';
import { useToast } from '../../context/ToastContext';
import { loginAdmin } from '../../services/authService';
import { pageVariants, pageTransition, fadeUp, staggerContainer } from '../../animations/pageTransition';
import styles from './AdminLogin.module.css';

const AdminLogin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { addToast } = useToast();

  const validate = () => {
    const e = {};
    if (!username.trim()) e.username = 'Required';
    if (!password) e.password = 'Required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await loginAdmin({ username, password });
      addToast(res.message, 'success');
    } catch {
      addToast('Login failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div className={styles.page} variants={pageVariants} initial="initial" animate="animate" exit="exit" transition={pageTransition}>
      <ThemeToggle />
      <Loader visible={loading} />
      <div className={styles.scanlines} />
      <Card>
        <motion.div variants={staggerContainer} initial="initial" animate="animate">
          <motion.div className={styles.header} variants={fadeUp}>
            <div className={styles.icon}><HiShieldCheck size={28} /></div>
            <h1 className={styles.title}>Admin Portal</h1>
            <p className={styles.subtitle}>Authorized personnel only</p>
          </motion.div>
          <motion.form onSubmit={handleSubmit} variants={fadeUp}>
            <Input label="Username" value={username} onChange={e => setUsername(e.target.value)} error={errors.username} />
            <Input label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} error={errors.password} />
            <Button type="submit" fullWidth loading={loading}>Authenticate</Button>
          </motion.form>
          <motion.div className={styles.footer} variants={fadeUp}>
            <Link to="/" className={styles.back}>← Back to Student Login</Link>
          </motion.div>
        </motion.div>
      </Card>
    </motion.div>
  );
};

export default AdminLogin;
