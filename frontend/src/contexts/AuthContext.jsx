import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Create context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
};

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Check for existing user session on mount
  useEffect(() => {
    // In a real app, this would verify the token with the backend
    const token = localStorage.getItem('authToken');
    const userJson = localStorage.getItem('user');
    
    if (token && userJson) {
      try {
        const user = JSON.parse(userJson);
        setCurrentUser(user);
      } catch (err) {
        console.error('Failed to parse user data:', err);
        logout();
      }
    }
    
    setLoading(false);
  }, []);

  // Login function
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, this would be an API call
      // For demo purposes, we'll simulate a successful login
      const response = await simulateApiCall({
        email,
        password
      });
      
      if (response.success) {
        setCurrentUser(response.user);
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        navigate('/dashboard');
        return true;
      } else {
        setError(response.message || 'Login failed');
        return false;
      }
    } catch (err) {
      setError(err.message || 'An error occurred during login');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (email, username, password) => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, this would be an API call
      const response = await simulateApiCall({
        email,
        username,
        password
      });
      
      if (response.success) {
        // Auto-login after registration
        setCurrentUser(response.user);
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        navigate('/dashboard');
        return true;
      } else {
        setError(response.message || 'Registration failed');
        return false;
      }
    } catch (err) {
      setError(err.message || 'An error occurred during registration');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    navigate('/login');
  };

  // Helper function to simulate API calls (for demo only)
  const simulateApiCall = (data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        // For demo purposes, accept any credentials
        if (data.email && data.password) {
          resolve({
            success: true,
            token: 'demo-token-123456789',
            user: {
              id: '1',
              email: data.email,
              username: data.username || data.email.split('@')[0],
              wallet_address: '0x71C7656EC7ab88b098defB751B7401B5f6d8976F'
            }
          });
        } else {
          resolve({
            success: false,
            message: 'Invalid credentials'
          });
        }
      }, 800); // Simulate network delay
    });
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};