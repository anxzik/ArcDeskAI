import React from 'react';
import Layout from '@/components/Layout';
import { Bot, Plus, MoreVertical, Terminal, Cpu, Zap } from 'lucide-react';
import useStore from '@/store';

const AgentsPage = () => {
  const { currentOrganization } = useStore();

  const dummyAgents = [
    { id: 1, name: 'Security Audit Bot', model: 'GPT-4o', status: 'Active', tools: 12, memory: 'Long-term' },
    { id: 2, name: 'Frontend Refactor Agent', model: 'Claude 3.5 Sonnet', status: 'Idle', tools: 5, memory: 'Buffer' },
    { id: 3, name: 'DevOps Automator', model: 'GPT-4o', status: 'Active', tools: 24, memory: 'None' },
  ];

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-2">AI Agents</h2>
            <p className="text-slate-400">Deploy and manage your specialized agent team for {currentOrganization?.name || 'your organization'}.</p>
          </div>
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Plus size={18} />
            <span>Create Agent</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dummyAgents.map((agent) => (
            <div key={agent.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:shadow-xl transition-all group">
              <div className="flex justify-between items-start mb-6">
                <div className="p-3 bg-blue-900/30 rounded-xl text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  <Bot size={28} />
                </div>
                <button className="p-1 text-slate-500 hover:text-white">
                  <MoreVertical size={20} />
                </button>
              </div>
              
              <h3 className="text-xl font-bold mb-1">{agent.name}</h3>
              <p className="text-slate-500 text-xs font-mono mb-4">{agent.model}</p>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                  <div className="flex items-center text-slate-500 text-[10px] uppercase font-bold tracking-wider mb-1">
                    <Terminal size={12} className="mr-1" /> Tools
                  </div>
                  <div className="text-lg font-bold">{agent.tools}</div>
                </div>
                <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                  <div className="flex items-center text-slate-500 text-[10px] uppercase font-bold tracking-wider mb-1">
                    <Cpu size={12} className="mr-1" /> Memory
                  </div>
                  <div className="text-lg font-bold text-sm truncate">{agent.memory}</div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-700">
                <div className="flex items-center">
                  <span className={`h-2 w-2 rounded-full mr-2 ${agent.status === 'Active' ? 'bg-emerald-500' : 'bg-slate-500'}`}></span>
                  <span className="text-sm font-medium text-slate-300">{agent.status}</span>
                </div>
                <button className="flex items-center text-blue-400 text-sm font-bold hover:text-blue-300 transition-colors">
                  <Zap size={14} className="mr-1" /> Run
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default AgentsPage;
