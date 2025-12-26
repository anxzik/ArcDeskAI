import React, { useEffect, useState } from 'react';
import { getAgents } from '../services/api';
import { Shield, Code, Server, Bot } from 'lucide-react';

const AgentCard = ({ agent }) => {
  const getIcon = (role) => {
    const r = role.toLowerCase();
    if (r.includes('cto') || r.includes('executive')) return Shield;
    if (r.includes('engineer') || r.includes('dev')) return Code;
    return Bot;
  };

  const Icon = getIcon(agent.role);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
            <Icon className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white">{agent.title}</h3>
            <span className="text-xs text-slate-500 uppercase tracking-wider">{agent.role}</span>
          </div>
        </div>
        <div className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-xs font-mono text-slate-400">
          {agent.desk_id}
        </div>
      </div>

      <div className="space-y-2">
        <div className="text-xs text-slate-500 uppercase font-semibold">Capabilities</div>
        <div className="flex flex-wrap gap-2">
          {agent.capabilities.map((cap) => (
            <span key={cap} className="px-2 py-1 rounded-md bg-slate-800 text-slate-300 text-xs border border-slate-700">
              {cap}
            </span>
          ))}
        </div>
      </div>
      
      {agent.reports_to && (
        <div className="pt-4 mt-auto border-t border-slate-800">
           <span className="text-xs text-slate-500">Reports to: </span>
           <span className="text-xs text-blue-400">{agent.reports_to}</span>
        </div>
      )}
    </div>
  );
};

const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await getAgents();
        setAgents(data);
      } catch (error) {
        console.error("Failed to fetch agents", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Agents</h2>
          <p className="text-slate-400 mt-2">Manage your AI workforce</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          Deploy Agent
        </button>
      </div>

      {loading ? (
        <div className="text-slate-400">Loading agents...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <AgentCard key={agent.desk_id} agent={agent} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Agents;
