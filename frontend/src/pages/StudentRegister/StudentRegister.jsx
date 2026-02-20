import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiUserAdd } from 'react-icons/hi';
import Input from '../../components/Input/Input';
import Button from '../../components/Button/Button';
import Card from '../../components/Card/Card';
import Loader from '../../components/Loader/Loader';
import ThemeToggle from '../../components/ThemeToggle/ThemeToggle';
import { useToast } from '../../context/ToastContext';
import { registerStudent } from '../../services/authService';
import { pageVariants, pageTransition, fadeUp, staggerContainer } from '../../animations/pageTransition';
import styles from './StudentRegister.module.css';

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

const StudentRegister = () => {
  const [form, setForm] = useState({
    fullName: '', usn: '', semester: '', email: '',
    contact: '', password: '', confirmPassword: '', terms: false,
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { addToast } = useToast();
  const strength = useMemo(() => getStrength(form.password), [form.password]);

  const set = (key) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setForm(prev => ({ ...prev, [key]: val }));
  };

  const validate = () => {
    const e = {};
    if (!form.fullName.trim()) e.fullName = 'Required';
    if (!form.usn.trim()) e.usn = 'Required';
    if (!form.semester) e.semester = 'Select semester';
    if (!form.email.includes('@')) e.email = 'Invalid email';
    if (form.contact.length < 10) e.contact = 'Invalid contact';
    if (form.password.length < 6) e.password = 'Min 6 characters';
    if (form.password !== form.confirmPassword) e.confirmPassword = 'Passwords do not match';
    if (!form.terms) e.terms = 'Accept the terms';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await registerStudent(form);
      addToast(res.message, 'success');
    } catch {
      addToast('Registration failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div className={styles.page} variants={pageVariants} initial="initial" animate="animate" exit="exit" transition={pageTransition}>
      <ThemeToggle />
      <Loader visible={loading} />
      <Card className={styles.wideCard}>
        <motion.div variants={staggerContainer} initial="initial" animate="animate">
          <motion.div className={styles.header} variants={fadeUp}>
            <div className={styles.icon}><HiUserAdd size={28} /></div>
            <h1 className={styles.title}>Create Account</h1>
            <p className={styles.subtitle}>Join the student portal</p>
          </motion.div>
          <motion.form onSubmit={handleSubmit} variants={fadeUp}>
            <div className={styles.grid}>
              <Input label="Full Name" value={form.fullName} onChange={set('fullName')} error={errors.fullName} />
              <Input label="USN" value={form.usn} onChange={set('usn')} error={errors.usn} />
            </div>
            <div className={styles.selectWrap}>
              <select className={styles.select} value={form.semester} onChange={set('semester')}>
                <option value="">Select Semester</option>
                {[1,2,3,4,5,6,7,8].map(s => <option key={s} value={s}>Semester {s}</option>)}
              </select>
              {errors.semester && <span className={styles.errorText}>{errors.semester}</span>}
            </div>
            <div className={styles.grid}>
              <Input label="Email" type="email" value={form.email} onChange={set('email')} error={errors.email} />
              <Input label="Contact" value={form.contact} onChange={set('contact')} error={errors.contact} />
            </div>
            <Input label="Password" type="password" value={form.password} onChange={set('password')} error={errors.password} />
            {form.password && (
              <div className={styles.strengthBar}>
                <div className={styles.strengthTrack}>
                  <motion.div
                    className={styles.strengthFill}
                    initial={{ width: 0 }}
                    animate={{ width: `${(strength / 4) * 100}%`, backgroundColor: strengthColors[strength - 1] || '#ef4444' }}
                    transition={{ duration: 0.4 }}
                  />
                </div>
                <span className={styles.strengthLabel} style={{ color: strengthColors[strength - 1] }}>
                  {strengthLabels[strength - 1] || 'Too short'}
                </span>
              </div>
            )}
            <Input label="Confirm Password" type="password" value={form.confirmPassword} onChange={set('confirmPassword')} error={errors.confirmPassword} />
            {form.confirmPassword && form.password === form.confirmPassword && (
              <motion.span className={styles.match} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>✓ Passwords match</motion.span>
            )}
            <label className={styles.checkbox}>
              <input type="checkbox" checked={form.terms} onChange={set('terms')} />
              <span>I accept the Terms &amp; Conditions</span>
            </label>
            {errors.terms && <span className={styles.errorText}>{errors.terms}</span>}
            <Button type="submit" fullWidth loading={loading}>Register</Button>
          </motion.form>
          <motion.div className={styles.footer} variants={fadeUp}>
            <Link to="/" className={styles.link}>Already have an account? Sign In</Link>
          </motion.div>
        </motion.div>
      </Card>
    </motion.div>
  );
};

export default StudentRegister;
