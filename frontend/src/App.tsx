import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import Loader from "@/components/auth/Loader";

const StudentLogin = lazy(() => import("./pages/StudentLogin"));
const LecturerLogin = lazy(() => import("./pages/LecturerLogin"));
const AdminLogin = lazy(() => import("./pages/AdminLogin"));
const StudentRegistration = lazy(() => import("./pages/StudentRegistration"));
const ForgotPassword = lazy(() => import("./pages/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/ResetPassword"));
const NotFound = lazy(() => import("./pages/NotFound"));

const App = () => (
  <ThemeProvider>
    <BrowserRouter>
      <Suspense fallback={<Loader />}>
        <Routes>
          <Route path="/" element={<StudentLogin />} />
          <Route path="/student-login" element={<StudentLogin />} />
          <Route path="/lecturer-login" element={<LecturerLogin />} />
          <Route path="/admin-login" element={<AdminLogin />} />
          <Route path="/register" element={<StudentRegistration />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  </ThemeProvider>
);

export default App;
