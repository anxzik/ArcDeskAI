import React, { useState } from 'react';
import Layout from '@/components/Layout';
import { Search, Plus, ExternalLink, ShieldCheck } from 'lucide-react';

const MCP_SERVERS = [
  { id: 1, name: 'GitHub MCP', description: 'Interact with GitHub repositories, issues, and PRs.', status: 'Installed' },
  { id: 2, name: 'Google Search MCP', description: 'Perform real-time web searches.', status: 'Available' },
  { id: 3, name: 'File System MCP', description: 'Secure access to local files.', status: 'Installed' },
  { id: 4, name: 'Slack MCP', description: 'Send messages and monitor channels.', status: 'Available' },
];

const MCPPage = () => {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">MCP Servers</h2>
          <p className="text-slate-400">Search and implement Model Context Protocol servers to extend your agents' capabilities.</p>
        </div>

        <div className="relative mb-8">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
          <input
            type="text"
            placeholder="Search for MCP servers (e.g., Notion, Postgres, Gmail)..."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {MCP_SERVERS.map((server) => (
            <div key={server.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-slate-500 transition-colors">
              <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-blue-900/30 rounded-lg text-blue-400">
                  <ShieldCheck size={24} />
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  server.status === 'Installed' ? 'bg-green-900/30 text-green-400' : 'bg-slate-700 text-slate-300'
                }`}>
                  {server.status}
                </span>
              </div>
              <h3 className="text-xl font-bold mb-2">{server.name}</h3>
              <p className="text-slate-400 text-sm mb-6">{server.description}</p>
              <div className="flex space-x-2">
                {server.status === 'Available' ? (
                  <button className="flex-grow flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 py-2 rounded-lg text-sm font-medium transition-colors">
                    <Plus size={16} />
                    <span>Install</span>
                  </button>
                ) : (
                  <button className="flex-grow flex items-center justify-center space-x-2 bg-slate-700 hover:bg-slate-600 py-2 rounded-lg text-sm font-medium transition-colors">
                    <span>Configure</span>
                  </button>
                )}
                <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg">
                  <ExternalLink size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default MCPPage;
