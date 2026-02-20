import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiBookOpen } from 'react-icons/hi';
import Input from '../../components/Input/Input';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import Loader from '../../components/Loader/Loader';
import ThemeToggle from '../../components/ThemeToggle/ThemeToggle';
import { useToast } from '../../context/ToastContext';
import { loginLecturer } from '../../services/authService';
import { pageVariants, pageTransition, fadeUp, staggerContainer } from '../../animations/pageTransition';
import styles from './LecturerLogin.module.css';

const LecturerLogin = () => {
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
      const res = await loginLecturer({ username, password });
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
      <Card>
        <motion.div variants={staggerContainer} initial="initial" animate="animate">
          <motion.div className={styles.header} variants={fadeUp}>
            <div className={styles.icon}><HiBookOpen size={28} /></div>
            <h1 className={styles.title}>Lecturer Portal</h1>
            <p className={styles.subtitle}>Faculty access only</p>
          </motion.div>
          <motion.form onSubmit={handleSubmit} variants={fadeUp}>
            <Input label="Username" value={username} onChange={e => setUsername(e.target.value)} error={errors.username} />
            <Input label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} error={errors.password} />
            <Button type="submit" fullWidth loading={loading}>Sign In</Button>
          </motion.form>
          <motion.div className={styles.links} variants={fadeUp}>
            <Link to="/forgot" className={styles.link}>Forgot Password?</Link>
            <Link to="/" className={styles.link}>← Student Login</Link>
          </motion.div>
        </motion.div>
      </Card>
    </motion.div>
  );
};

export default LecturerLogin;
