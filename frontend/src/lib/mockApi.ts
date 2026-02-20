export const mockFetch = (endpoint: string, _data?: Record<string, unknown>): Promise<{ ok: boolean; message: string }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      switch (endpoint) {
        case "/api/login":
          resolve({ ok: true, message: "Login successful!" });
          break;
        case "/api/register":
          resolve({ ok: true, message: "Registration successful!" });
          break;
        case "/api/forgot-password":
          resolve({ ok: true, message: "Reset link sent to your email" });
          break;
        case "/api/reset-password":
          resolve({ ok: true, message: "Password reset successful!" });
          break;
        default:
          resolve({ ok: false, message: "Unknown endpoint" });
      }
    }, 1500);
  });
};
