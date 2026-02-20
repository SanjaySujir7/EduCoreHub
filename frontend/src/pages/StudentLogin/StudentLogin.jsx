import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiAcademicCap } from 'react-icons/hi';
import Input from '../../components/Input/Input';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import Loader from '../../components/Loader/Loader';
import ThemeToggle from '../../components/ThemeToggle/ThemeToggle';
import { useAccess } from '../../context/AccessContext';
import { useToast } from '../../context/ToastContext';
import { loginStudent } from '../../services/authService';
import { pageVariants, pageTransition, fadeUp, staggerContainer } from '../../animations/pageTransition';
import styles from './StudentLogin.module.css';

const StudentLogin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { grantAccess } = useAccess();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const validate = () => {
    const e = {};
    if (!username.trim()) e.username = 'Username is required';
    if (!password) e.password = 'Password is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await loginStudent({ username, password });
      addToast(res.message, 'success');
    } catch {
      addToast('Login failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const goToLecturer = () => { grantAccess('lecturer'); navigate('/lecturer-login'); };
  const goToAdmin = () => { grantAccess('admin'); navigate('/admin-login'); };

  return (
    <motion.div className={styles.page} variants={pageVariants} initial="initial" animate="animate" exit="exit" transition={pageTransition}>
      <ThemeToggle />
      <Loader visible={loading} />
      <div className={styles.bgOrbs}>
        <div className={styles.orb1} />
        <div className={styles.orb2} />
        <div className={styles.orb3} />
      </div>
      <Card>
        <motion.div variants={staggerContainer} initial="initial" animate="animate">
          <motion.div className={styles.header} variants={fadeUp}>
            <div className={styles.icon}><HiAcademicCap size={32} /></div>
            <h1 className={styles.title}>Student Portal</h1>
            <p className={styles.subtitle}>Sign in to continue</p>
          </motion.div>
          <motion.form onSubmit={handleSubmit} variants={fadeUp}>
            <Input label="Username" value={username} onChange={e => setUsername(e.target.value)} error={errors.username} />
            <Input label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} error={errors.password} />
            <Button type="submit" fullWidth loading={loading}>Sign In</Button>
          </motion.form>
          <motion.div className={styles.links} variants={fadeUp}>
            <Link to="/register" className={styles.link}>Create Account</Link>
            <Link to="/forgot" className={styles.link}>Forgot Password?</Link>
          </motion.div>
          {/* <motion.div className={styles.divider} variants={fadeUp}>
            <span>Other Portals</span>
          </motion.div>
          <motion.div className={styles.portalLinks} variants={fadeUp}>
            <button className={styles.portalBtn} onClick={goToLecturer}>Lecturer Login</button>
            <button className={styles.portalBtn} onClick={goToAdmin}>Admin Login</button>
          </motion.div> */}
        </motion.div>
      </Card>
    </motion.div>
  );
};

export default StudentLogin;
