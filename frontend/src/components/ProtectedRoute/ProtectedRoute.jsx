import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAccess } from '../../context/AccessContext';

const ProtectedRoute = ({ role, children }) => {
  const { accessRole } = useAccess();
  if (accessRole !== role) return <Navigate to="/" replace />;
  return children;
};

export default ProtectedRoute;
