import { useState, useEffect, createContext, useContext } from 'react';
  
  const AuthContext = createContext(null);
  
  export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
  
    useEffect(() => {
      checkAuth();
    }, []);
  
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setLoading(false);
          return;
        }
  
        const response = await fetch('/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
  
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          localStorage.removeItem('token');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };
  
    const login = async (credentials) => {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });
  
      if (!response.ok) {
        throw new Error('Login failed');
      }
  
      const data = await response.json();
      localStorage.setItem('token', data.token);
      await checkAuth();
    };
  
    const logout = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
        }
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        localStorage.removeItem('token');
        setUser(null);
        window.location.href = '/login';
      }
    };
  
    const value = {
      user,
      loading,
      login,
      logout,
      checkAuth
    };
  
    return (
      <AuthContext.Provider value={value}>
        {children}
      </AuthContext.Provider>
    );
  };
  
  export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
      throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
  };
  
  // Protected Route Component
  export const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    const [redirecting, setRedirecting] = useState(false);
  
    useEffect(() => {
      if (!loading && !user) {
        setRedirecting(true);
        window.location.href = `/login?redirect=${window.location.pathname}`;
      }
    }, [user, loading]);
  
    if (loading || redirecting) {
      return <div>Loading...</div>;
    }
  
    return children;
  };