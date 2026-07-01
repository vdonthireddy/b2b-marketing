import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '@/stores/authStore';
import { User } from '@/types/user';

describe('Auth Store', () => {
  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    name: 'Test User',
    team_id: 'team-1',
    team_name: 'Test Team',
    role: 'admin',
    is_active: true
  };

  beforeEach(() => {
    useAuthStore.getState().logout();
  });

  it('initial state should be unauthenticated', () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
  });

  it('setAuth should update state correctly', () => {
    useAuthStore.getState().setAuth('access-token', 'refresh-token', mockUser);
    
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user).toEqual(mockUser);
    expect(state.accessToken).toBe('access-token');
    expect(state.refreshToken).toBe('refresh-token');
  });

  it('logout should reset state', () => {
    useAuthStore.getState().setAuth('access-token', 'refresh-token', mockUser);
    useAuthStore.getState().logout();
    
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
  });
});
