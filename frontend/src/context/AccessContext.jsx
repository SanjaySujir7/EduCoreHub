import React, { createContext, useState, useContext } from 'react';

const AccessContext = createContext();

export const useAccess = () => useContext(AccessContext);

export const AccessProvider = ({ children }) => {
  const [accessRole, setAccessRole] = useState(null);

  const grantAccess = (role) => setAccessRole(role);
  const clearAccess = () => setAccessRole(null);

  return (
    <AccessContext.Provider value={{ accessRole, grantAccess, clearAccess }}>
      {children}
    </AccessContext.Provider>
  );
};
