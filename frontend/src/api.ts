/**
 * API client for the Hazard Alert backend.
 */

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API error');
  }
  return res.json();
}

// ── People ──────────────────────────────────────────────────
export const api = {
  // People
  getPeople: (params?: URLSearchParams) => request<any[]>(`/people?${params || ''}`),
  getPeopleCount: () => request<{ count: number }>('/people/count'),
  getDistricts: () => request<string[]>('/people/districts'),
  getUpazilas: (district?: string) => request<string[]>(`/people/upazilas${district ? `?district=${district}` : ''}`),
  getPerson: (id: string) => request<any>(`/people/${id}`),

  // Events
  getEvents: () => request<any[]>('/events'),
  createEvent: (data: any) => request<any>('/events', { method: 'POST', body: JSON.stringify(data) }),

  // Campaigns
  getCampaigns: () => request<any[]>('/campaigns'),
  createCampaign: (data: any) => request<any>('/campaigns', { method: 'POST', body: JSON.stringify(data) }),
  startCampaign: (id: string) => request<any>(`/campaigns/${id}/start`, { method: 'POST' }),
  getCampaign: (id: string) => request<any>(`/campaigns/${id}`),

  // Calls
  createCall: (data: any) => request<any>('/calls', { method: 'POST', body: JSON.stringify(data) }),
  startCall: (id: string) => request<any>(`/calls/${id}/start`, { method: 'POST' }),
  chatTurn: (id: string, data: any) => request<any>(`/calls/${id}/chat`, { method: 'POST', body: JSON.stringify(data) }),
  endCall: (id: string) => request<any>(`/calls/${id}/end`, { method: 'POST' }),
  getCall: (id: string) => request<any>(`/calls/${id}`),
  getCallTurns: (id: string) => request<any[]>(`/calls/${id}/turns`),

  // Analytics
  getDashboardStats: () => request<any>('/analytics/dashboard'),

  // Map
  getMapGeoJSON: (params?: URLSearchParams) => request<any>(`/map/geojson?${params || ''}`),

  // Health
  getHealth: () => request<any>('/health'),
};
