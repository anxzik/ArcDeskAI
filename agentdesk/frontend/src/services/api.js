const API_URL = '';

export const getAgents = async () => {
  const response = await fetch(`/agents/`);
  return response.json();
};

export const createAgent = async (agent) => {
  const response = await fetch(`/agents/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(agent),
  });
  return response.json();
};
