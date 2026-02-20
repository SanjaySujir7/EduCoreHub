import React, { useState } from "react";
import { motion } from "framer-motion";
import AuthCard from "@/components/auth/AuthCard";
import AnimatedInput from "@/components/auth/AnimatedInput";
import GlowButton from "@/components/auth/GlowButton";
import ToastNotification from "@/components/auth/ToastNotification";
import { mockFetch } from "@/lib/mockApi";
import { ShieldCheck } from "lucide-react";

const AdminLogin: React.FC = () => {
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
        title="Admin Control Center"
        subtitle="Authorized personnel only"
        variant="admin"
        icon={<div className="w-14 h-14 rounded-2xl bg-destructive/10 border border-destructive/20 flex items-center justify-center glow-admin"><ShieldCheck className="text-destructive" size={28} /></div>}
      >
        <motion.div className="space-y-4" initial="hidden" animate="show" variants={{ hidden: {}, show: { transition: { staggerChildren: 0.1 } } }}>
          <AnimatedInput label="Admin Username" value={username} onChange={setUsername} />
          <AnimatedInput label="Password" type="password" value={password} onChange={setPassword} />
          <GlowButton onClick={handleLogin} loading={loading} variant="admin">
            Access Dashboard
          </GlowButton>
        </motion.div>

        {/* Scan line effect */}
        <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
          <div className="w-full h-[1px] bg-destructive/20 animate-scan-line" />
        </div>
      </AuthCard>
    </>
  );
};

export default AdminLogin;
