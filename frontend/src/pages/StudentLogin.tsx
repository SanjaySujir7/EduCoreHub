import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import AuthCard from "@/components/auth/AuthCard";
import AnimatedInput from "@/components/auth/AnimatedInput";
import GlowButton from "@/components/auth/GlowButton";
import ToastNotification from "@/components/auth/ToastNotification";
import { mockFetch } from "@/lib/mockApi";
import { GraduationCap } from "lucide-react";

const StudentLogin: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: "" });

  const handleLogin = async () => {
    setLoading(true);
    const res = await mockFetch("/api/login", { username, password });
    setLoading(false);
    setToast({ show: true, message: res.message });
    setTimeout(() => setToast({ show: false, message: "" }), 3000);
  };

  return (
    <>
      <ToastNotification message={toast.message} show={toast.show} onClose={() => setToast({ show: false, message: "" })} />
      <AuthCard
        title="Student Portal"
        subtitle="Sign in to access your dashboard"
        variant="student"
        icon={<div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center glow-primary"><GraduationCap className="text-primary" size={28} /></div>}
      >
        <motion.div className="space-y-4" initial="hidden" animate="show" variants={{ hidden: {}, show: { transition: { staggerChildren: 0.1 } } }}>
          <AnimatedInput label="Username" value={username} onChange={setUsername} />
          <AnimatedInput label="Password" type="password" value={password} onChange={setPassword} />
          <GlowButton onClick={handleLogin} loading={loading} variant="primary">
            Sign In
          </GlowButton>
        </motion.div>
        <div className="flex flex-col items-center gap-2 pt-2 text-sm">
          <NavLink to="/register" className="text-primary hover:underline transition-all">
            New user? Sign up
          </NavLink>
          <NavLink to="/forgot-password" className="text-muted-foreground hover:text-primary transition-all">
            Forgot password?
          </NavLink>
        </div>
      </AuthCard>
    </>
  );
};

export default StudentLogin;
