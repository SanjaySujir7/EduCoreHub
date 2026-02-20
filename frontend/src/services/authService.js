// Mock backend — replace with real API calls via request() when backend is ready
const mock = (data, delay = 1500) =>
  new Promise((resolve) => setTimeout(() => resolve({ success: true, ...data }), delay));

export const loginStudent = (data) =>
  mock({ message: 'Student login successful', user: { role: 'student', username: data.username } });

export const loginLecturer = (data) =>
  mock({ message: 'Lecturer login successful', user: { role: 'lecturer', username: data.username } });

export const loginAdmin = (data) =>
  mock({ message: 'Admin login successful', user: { role: 'admin', username: data.username } });

export const registerStudent = (data) =>
  mock({ message: 'Registration successful', user: { name: data.fullName } });

export const forgotPassword = (data) =>
  mock({ message: 'Reset link sent to registered email' });

export const resetPassword = (data) =>
  mock({ message: 'Password reset successful' });
