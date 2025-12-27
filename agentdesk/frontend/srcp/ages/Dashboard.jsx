import React, { useEffect } from 'react';
import Layout from '../components/Layout';
import useStore from '../store';
import { getAgents, createAgent } from '../services/api';

const Dashboard = () => {
  const agents = useStore((state) => state.agents);
  const addAgent = useStore((state) => state.addAgent);

  useEffect(() => {
    const fetchAgents = async () => {
      const agents = await getAgents();
      agents.forEach(addAgent);
    };
    fetchAgents();
  }, [addAgent]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newAgent = {
      name: e.target.name.value,
      description: e.target.description.value,
    };
    const createdAgent = await createAgent(newAgent);
    addAgent(createdAgent);
    e.target.reset();
  };

  return (
    <Layout>
      <h2 className="text-xl mb-4">Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-slate-800 p-4 rounded">
          <h3 className="text-lg">Agents</h3>
          <ul>
            {agents.map((agent) => (
              <li key={agent.id}>{agent.name}</li>
            ))}
          </ul>
          <form onSubmit={handleSubmit} className="mt-4">
            <input
              type="text"
              name="name"
              placeholder="Agent Name"
              className="bg-slate-700 p-2 rounded w-full mb-2"
            />
            <textarea
              name="description"
              placeholder="Agent Description"
              className="bg-slate-700 p-2 rounded w-full"
            ></textarea>
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-2"
            >
              Create Agent
            </button>
          </form>
        </div>
        <div className="bg-slate-800 p-4 rounded">
          <h3 className="text-lg">Knowledge Bases</h3>
          <p>Manage your knowledge bases.</p>
        </div>
        <div className="bg-slate-800 p-4 rounded">
          <h3 className="text-lg">MCP Search</h3>
          <p>Search the MCP server.</p>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
