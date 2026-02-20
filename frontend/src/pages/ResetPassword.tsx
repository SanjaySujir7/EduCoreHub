import React, { useState, useMemo } from "react";
import { motion } from "framer-motion";
import AuthCard from "@/components/auth/AuthCard";
import AnimatedInput from "@/components/auth/AnimatedInput";
import GlowButton from "@/components/auth/GlowButton";
import ToastNotification from "@/components/auth/ToastNotification";
import { mockFetch } from "@/lib/mockApi";
import { Lock } from "lucide-react";

const getStrength = (pw: string): { score: number; label: string; color: string } => {
  let score = 0;
  if (pw.length >= 6) score++;
  if (pw.length >= 10) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;

  if (score <= 1) return { score, label: "Weak", color: "bg-destructive" };
  if (score <= 3) return { score, label: "Medium", color: "bg-yellow-500" };
  return { score, label: "Strong", color: "bg-primary" };
};

const ResetPassword: React.FC = () => {
  const [email] = useState("student@university.edu");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: "" });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const strength = useMemo(() => getStrength(password), [password]);

  const handleSubmit = async () => {
    const e: Record<string, string> = {};
    if (password.length < 6) e.password = "Min 6 characters";
    if (password !== confirmPassword) e.confirmPassword = "Passwords don't match";
    setErrors(e);
    if (Object.keys(e).length > 0) return;

    setLoading(true);
    const res = await mockFetch("/api/reset-password", { email, password });
    setLoading(false);
    setToast({ show: true, message: res.message });
    setTimeout(() => setToast({ show: false, message: "" }), 3000);
  };

  return (
    <>
      <ToastNotification message={toast.message} show={toast.show} onClose={() => setToast({ show: false, message: "" })} />
      <AuthCard
        title="Reset Password"
        subtitle="Choose a new secure password"
        variant="student"
        icon={<div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center glow-primary"><Lock className="text-primary" size={28} /></div>}
      >
        <motion.div className="space-y-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <AnimatedInput label="Email" value={email} onChange={() => {}} readOnly />
          <div className="space-y-2">
            <AnimatedInput label="New Password" type="password" value={password} onChange={(v) => { setPassword(v); setErrors(e => ({...e, password: ""})); }} error={errors.password} />
            {password && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="space-y-1">
                <div className="flex gap-1.5">
                  {[...Array(5)].map((_, i) => (
                    <motion.div
                      key={i}
                      className={`h-1.5 flex-1 rounded-full transition-colors duration-300 ${i < strength.score ? strength.color : "bg-muted"}`}
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: i * 0.05 }}
                    />
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">Strength: {strength.label}</p>
              </motion.div>
            )}
          </div>
          <AnimatedInput label="Confirm Password" type="password" value={confirmPassword} onChange={(v) => { setConfirmPassword(v); setErrors(e => ({...e, confirmPassword: ""})); }} error={errors.confirmPassword} />
          <GlowButton onClick={handleSubmit} loading={loading} variant="success">
            Reset Password
          </GlowButton>
        </motion.div>
      </AuthCard>
    </>
  );
};

export default ResetPassword;
