import React from 'react';
import Layout from '../components/Layout';

const Dashboard = () => {
  return (
    <Layout>
      <h2 className="text-xl mb-4">Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-slate-800 p-4 rounded">
          <h3 className="text-lg">Agents</h3>
          <p>Manage your AI agents.</p>
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
