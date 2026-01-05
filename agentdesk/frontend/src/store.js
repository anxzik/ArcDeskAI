import { create } from 'zustand';

const useStore = create((set) => ({
  user: null,
  organizations: [],
  currentOrganization: null,
  projects: [],
  agents: [],
  
  setUser: (user) => set({ user }),
  setOrganizations: (organizations) => set({ organizations }),
  setCurrentOrganization: (org) => set({ currentOrganization: org }),
  setProjects: (projects) => set({ projects }),
  setAgents: (agents) => set({ agents }),
  
  logout: () => set({ 
    user: null, 
    organizations: [], 
    currentOrganization: null, 
    projects: [], 
    agents: [] 
  }),
}));

export default useStore;