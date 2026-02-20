import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ThemeProvider } from './context/ThemeContext';
import { AccessProvider } from './context/AccessContext';
import { ToastProvider } from './context/ToastContext';
import Loader from './components/Loader/Loader';
import Toast from './components/Toast/Toast';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';

const StudentLogin = lazy(() => import('./pages/StudentLogin/StudentLogin'));
const StudentRegister = lazy(() => import('./pages/StudentRegister/StudentRegister'));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword/ForgotPassword'));
const ResetPassword = lazy(() => import('./pages/ResetPassword/ResetPassword'));
const LecturerLogin = lazy(() => import('./pages/LecturerLogin/LecturerLogin'));
const AdminLogin = lazy(() => import('./pages/AdminLogin/AdminLogin'));

const AnimatedRoutes = () => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<StudentLogin />} />
        <Route path="/register" element={<StudentRegister />} />
        <Route path="/forgot" element={<ForgotPassword />} />
        <Route path="/reset" element={<ResetPassword />} />
        <Route path="/lecturer-login" element={<ProtectedRoute role="lecturer"><LecturerLogin /></ProtectedRoute>} />
        <Route path="/admin-login" element={<ProtectedRoute role="admin"><AdminLogin /></ProtectedRoute>} />
      </Routes>
    </AnimatePresence>
  );
};

const App = () => (
  <ThemeProvider>
    <AccessProvider>
      <ToastProvider>
        <BrowserRouter>
          <Suspense fallback={<Loader visible />}>
            <AnimatedRoutes />
          </Suspense>
          <Toast />
        </BrowserRouter>
      </ToastProvider>
    </AccessProvider>
  </ThemeProvider>
);

export default App;
