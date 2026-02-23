import { createContext, useCallback, useEffect, useState, type ReactNode } from 'react';
import { createAnonymousUser, getProfile } from '@/services/api';

interface AuthUser {
  id: string;
  display_name: string;
  is_anonymous: boolean;
  email?: string;
  avatar_url?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  login: () => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loading: true,
  login: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const initAuth = useCallback(async () => {
    // Check for token in URL (from Google OAuth callback)
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    if (urlToken) {
      localStorage.setItem('token', urlToken);
      window.history.replaceState({}, '', window.location.pathname);
    }

    let existingToken = localStorage.getItem('token');

    if (!existingToken) {
      // Create anonymous user
      try {
        const data = await createAnonymousUser();
        existingToken = data.token;
        localStorage.setItem('token', data.token);
        setUser({
          id: data.user_id,
          display_name: data.display_name,
          is_anonymous: true,
        });
        setToken(data.token);
      } catch {
        console.error('Failed to create anonymous user');
      }
    } else {
      // Validate existing token by fetching profile
      try {
        const profile = await getProfile();
        if (profile.error) {
          // Token expired — create new anonymous user
          localStorage.removeItem('token');
          const data = await createAnonymousUser();
          existingToken = data.token;
          localStorage.setItem('token', data.token);
          setUser({
            id: data.user_id,
            display_name: data.display_name,
            is_anonymous: true,
          });
        } else {
          setUser({
            id: profile.id,
            display_name: profile.display_name,
            is_anonymous: profile.is_anonymous,
            email: profile.email,
            avatar_url: profile.avatar_url,
          });
        }
        setToken(existingToken);
      } catch {
        localStorage.removeItem('token');
      }
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  const login = async () => {
    await initAuth();
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setToken(null);
    window.location.href = '/';
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
