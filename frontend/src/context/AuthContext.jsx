/**
 * Authentication Context
 * Manages user auth state, tokens, and team context across the app.
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const AuthContext = createContext(null);

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const CURRENT_TEAM_KEY = 'current_team_id';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [teams, setTeams] = useState([]);
  const [currentTeam, setCurrentTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get stored tokens
  const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
  const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);
  const getCurrentTeamId = () => localStorage.getItem(CURRENT_TEAM_KEY);

  // Store tokens
  const storeTokens = (accessToken, refreshToken) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  };

  // Clear tokens
  const clearTokens = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(CURRENT_TEAM_KEY);
  };

  // Create axios instance with auth headers
  const authAxios = useCallback(() => {
    const instance = axios.create({
      baseURL: `${API}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth header
    instance.interceptors.request.use((config) => {
      const token = getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      const teamId = getCurrentTeamId();
      if (teamId) {
        config.headers['X-Team-ID'] = teamId;
      }
      return config;
    });

    // Handle 401 errors (token expired)
    instance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = getRefreshToken();
            if (refreshToken) {
              const response = await axios.post(`${API}/api/auth/refresh`, {
                refresh_token: refreshToken,
              });
              
              storeTokens(response.data.access_token, response.data.refresh_token);
              originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
              return instance(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout
            clearTokens();
            setUser(null);
            setTeams([]);
            setCurrentTeam(null);
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(error);
      }
    );

    return instance;
  }, []);

  // Fetch user info
  const fetchUser = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return null;
    }

    try {
      const response = await authAxios().get('/auth/me');
      setUser(response.data);
      setTeams(response.data.teams || []);
      
      // Set current team
      const storedTeamId = getCurrentTeamId();
      const teamList = response.data.teams || [];
      
      if (storedTeamId) {
        const team = teamList.find(t => t.id === storedTeamId);
        if (team) {
          setCurrentTeam(team);
        } else if (teamList.length > 0) {
          setCurrentTeam(teamList[0]);
          localStorage.setItem(CURRENT_TEAM_KEY, teamList[0].id);
        }
      } else if (teamList.length > 0) {
        setCurrentTeam(teamList[0]);
        localStorage.setItem(CURRENT_TEAM_KEY, teamList[0].id);
      }
      
      return response.data;
    } catch (err) {
      console.error('Failed to fetch user:', err);
      clearTokens();
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, [authAxios]);

  // Login
  const login = async (email, password) => {
    try {
      setError(null);
      const response = await axios.post(`${API}/api/auth/login`, {
        email,
        password,
      });

      const { access_token, refresh_token, user: userData, current_team } = response.data;
      
      storeTokens(access_token, refresh_token);
      setUser(userData);
      
      if (current_team) {
        setCurrentTeam(current_team);
        localStorage.setItem(CURRENT_TEAM_KEY, current_team.id);
      }
      
      // Fetch full user info with teams
      await fetchUser();
      
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      return { success: false, error: message };
    }
  };

  // Signup
  const signup = async (email, password, firstName, lastName) => {
    try {
      setError(null);
      const response = await axios.post(`${API}/api/auth/signup`, {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      });

      const { access_token, refresh_token, user: userData, current_team } = response.data;
      
      storeTokens(access_token, refresh_token);
      setUser(userData);
      
      if (current_team) {
        setCurrentTeam(current_team);
        setTeams([current_team]);
        localStorage.setItem(CURRENT_TEAM_KEY, current_team.id);
      }
      
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Signup failed';
      setError(message);
      return { success: false, error: message };
    }
  };

  // Logout
  const logout = async (logoutAll = false) => {
    try {
      const refreshToken = getRefreshToken();
      await authAxios().post('/auth/logout', null, {
        params: { logout_all: logoutAll, refresh_token: refreshToken },
      });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      clearTokens();
      setUser(null);
      setTeams([]);
      setCurrentTeam(null);
    }
  };

  // Switch team
  const switchTeam = (teamId) => {
    const team = teams.find(t => t.id === teamId);
    if (team) {
      setCurrentTeam(team);
      localStorage.setItem(CURRENT_TEAM_KEY, teamId);
    }
  };

  // Create team
  const createTeam = async (name, type = 'organization') => {
    try {
      const response = await authAxios().post('/teams', { name, type });
      const newTeam = { ...response.data, role: 'owner' };
      setTeams(prev => [...prev, newTeam]);
      return { success: true, team: newTeam };
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to create team';
      return { success: false, error: message };
    }
  };

  // Handle OAuth callback - called from OAuthCallbackPage
  const handleOAuthCallback = async (accessToken, refreshToken) => {
    // Store tokens
    storeTokens(accessToken, refreshToken);
    
    // Fetch user data
    await fetchUser();
  };

  // Refresh teams list (useful after accepting invite)
  const refreshTeams = async () => {
    try {
      const response = await authAxios().get('/auth/me');
      const userData = response.data;
      
      if (userData.teams && userData.teams.length > 0) {
        setTeams(userData.teams);
        
        // Update current team if needed
        const storedTeamId = getCurrentTeamId();
        const currentTeamExists = userData.teams.find(t => t.id === storedTeamId);
        
        if (!currentTeamExists) {
          setCurrentTeam(userData.teams[0]);
          localStorage.setItem(CURRENT_TEAM_KEY, userData.teams[0].id);
        } else if (currentTeam && currentTeamExists) {
          setCurrentTeam(currentTeamExists);
        }
      }
    } catch (err) {
      console.error('Failed to refresh teams:', err);
    }
  };

  // Get OAuth providers configuration
  const getOAuthProviders = async () => {
    try {
      const response = await axios.get(`${API}/api/auth/oauth/providers`);
      return response.data.providers;
    } catch (err) {
      console.error('Failed to get OAuth providers:', err);
      return [];
    }
  };

  // Initiate OAuth login
  const initiateOAuthLogin = (provider) => {
    window.location.href = `${API}/api/auth/oauth/${provider}/redirect`;
  };

  // Initialize auth state
  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const value = {
    user,
    teams,
    currentTeam,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    signup,
    logout,
    switchTeam,
    createTeam,
    fetchUser,
    authAxios,
    getAccessToken,
    getCurrentTeamId,
    handleOAuthCallback,
    refreshTeams,
    getOAuthProviders,
    initiateOAuthLogin,
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

export default AuthContext;
