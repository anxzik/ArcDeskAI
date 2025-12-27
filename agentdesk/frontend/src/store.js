import create from 'zustand';

const useStore = create((set) => ({
  agents: [],
  addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
}));

export default useStore;
