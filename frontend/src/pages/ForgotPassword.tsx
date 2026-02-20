import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import AuthCard from "@/components/auth/AuthCard";
import AnimatedInput from "@/components/auth/AnimatedInput";
import GlowButton from "@/components/auth/GlowButton";
import ToastNotification from "@/components/auth/ToastNotification";
import { mockFetch } from "@/lib/mockApi";
import { KeyRound } from "lucide-react";

const ForgotPassword: React.FC = () => {
  const [usn, setUsn] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: "" });

  const handleSubmit = async () => {
    if (!usn) return;
    setLoading(true);
    const res = await mockFetch("/api/forgot-password", { usn });
    setLoading(false);
    setToast({ show: true, message: res.message });
    setTimeout(() => setToast({ show: false, message: "" }), 4000);
  };

  return (
    <>
      <ToastNotification message={toast.message} show={toast.show} onClose={() => setToast({ show: false, message: "" })} />
      <AuthCard
        title="Forgot Password"
        subtitle="Enter your USN to receive a reset link"
        variant="student"
        icon={<div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center animate-float"><KeyRound className="text-primary" size={28} /></div>}
      >
        <motion.div className="space-y-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <AnimatedInput label="USN Number" value={usn} onChange={setUsn} />
          <GlowButton onClick={handleSubmit} loading={loading} variant="primary">
            Send Reset Link
          </GlowButton>
        </motion.div>
        <div className="text-center pt-2 text-sm">
          <NavLink to="/student-login" className="text-muted-foreground hover:text-primary transition-all">
            ← Back to Login
          </NavLink>
        </div>
      </AuthCard>
    </>
  );
};

export default ForgotPassword;
