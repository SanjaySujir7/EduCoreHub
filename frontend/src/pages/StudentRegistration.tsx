import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import AuthCard from "@/components/auth/AuthCard";
import AnimatedInput from "@/components/auth/AnimatedInput";
import GlowButton from "@/components/auth/GlowButton";
import ToastNotification from "@/components/auth/ToastNotification";
import { mockFetch } from "@/lib/mockApi";
import { UserPlus } from "lucide-react";

const semesters = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"];

const StudentRegistration: React.FC = () => {
  const [form, setForm] = useState({
    fullName: "", usn: "", semester: "", email: "", contact: "", password: "", confirmPassword: "",
  });
  const [accepted, setAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: "" });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const update = (key: string) => (val: string) => {
    setForm((f) => ({ ...f, [key]: val }));
    setErrors((e) => ({ ...e, [key]: "" }));
  };

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.fullName) e.fullName = "Required";
    if (!form.usn) e.usn = "Required";
    if (!form.semester) e.semester = "Select semester";
    if (!form.email || !form.email.includes("@")) e.email = "Valid email required";
    if (!form.contact || form.contact.length < 10) e.contact = "Valid number required";
    if (form.password.length < 6) e.password = "Min 6 characters";
    if (form.password !== form.confirmPassword) e.confirmPassword = "Passwords don't match";
    if (!accepted) e.terms = "Accept terms";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleRegister = async () => {
    if (!validate()) return;
    setLoading(true);
    const res = await mockFetch("/api/register", form);
    setLoading(false);
    setToast({ show: true, message: res.message });
    setTimeout(() => setToast({ show: false, message: "" }), 3000);
  };

  return (
    <>
      <ToastNotification message={toast.message} show={toast.show} onClose={() => setToast({ show: false, message: "" })} />
      <AuthCard
        title="Student Registration"
        subtitle="Create your account to get started"
        variant="student"
        icon={<div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center glow-primary"><UserPlus className="text-primary" size={28} /></div>}
      >
        <motion.div className="space-y-3" initial="hidden" animate="show" variants={{ hidden: {}, show: { transition: { staggerChildren: 0.07 } } }}>
          <AnimatedInput label="Full Name" value={form.fullName} onChange={update("fullName")} error={errors.fullName} />
          <AnimatedInput label="University Seat Number (USN)" value={form.usn} onChange={update("usn")} error={errors.usn} />

          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
            <select
              value={form.semester}
              onChange={(e) => { setForm(f => ({...f, semester: e.target.value})); setErrors(e2 => ({...e2, semester: ""})); }}
              className={`w-full px-4 py-3.5 rounded-xl bg-secondary/50 border text-foreground outline-none 
                transition-all duration-300 text-sm ${errors.semester ? "border-destructive" : "border-border"} 
                focus:border-primary focus:glow-primary`}
            >
              <option value="" className="bg-card text-foreground">Select Semester</option>
              {semesters.map((s) => (
                <option key={s} value={s} className="bg-card text-foreground">{s} Semester</option>
              ))}
            </select>
            {errors.semester && <p className="text-destructive text-xs mt-1 ml-1">{errors.semester}</p>}
          </motion.div>

          <AnimatedInput label="Email" type="email" value={form.email} onChange={update("email")} error={errors.email} />
          <AnimatedInput label="Contact Number" value={form.contact} onChange={update("contact")} error={errors.contact} />
          <AnimatedInput label="Password" type="password" value={form.password} onChange={update("password")} error={errors.password} />
          <AnimatedInput label="Confirm Password" type="password" value={form.confirmPassword} onChange={update("confirmPassword")} error={errors.confirmPassword} />

          <motion.label initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 cursor-pointer text-sm text-muted-foreground pt-1">
            <input type="checkbox" checked={accepted} onChange={(e) => setAccepted(e.target.checked)}
              className="w-4 h-4 rounded border-border accent-primary" />
            <span>I accept the Terms & Conditions</span>
          </motion.label>
          {errors.terms && <p className="text-destructive text-xs ml-6">{errors.terms}</p>}

          <GlowButton onClick={handleRegister} loading={loading} variant="primary">
            Create Account
          </GlowButton>
        </motion.div>

        <div className="text-center pt-2 text-sm">
          <NavLink to="/student-login" className="text-primary hover:underline transition-all">
            Already registered? Login here
          </NavLink>
        </div>
      </AuthCard>
    </>
  );
};

export default StudentRegistration;
