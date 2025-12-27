const API_URL = 'http://localhost:8000';

export const getAgents = async () => {
  const response = await fetch(`${API_URL}/agents`);
  return response.json();
};

export const createAgent = async (agent) => {
  const response = await fetch(`${API_URL}/agents`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(agent),
  });
  return response.json();
};
