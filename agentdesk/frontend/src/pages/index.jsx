import React from 'react';
import Layout from '@/components/Layout';
import useStore from '@/store';
import { Bot, FolderKanban, Workflow, Activity, Users, Plus } from 'lucide-react';
import Link from 'next/link';

const Dashboard = () => {
  const { user, currentOrganization } = useStore();

  if (!user) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <h2 className="text-4xl font-extrabold mb-4">Scale your AI Operations</h2>
          <p className="text-xl text-slate-400 mb-8 max-w-2xl">
            ArcDeskAI is the orchestration layer for your AI agents. Build, deploy, and monitor agentic teams in one unified workspace.
          </p>
          <Link href="/auth/login" className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-xl font-bold text-lg transition-all shadow-lg shadow-blue-500/20">
            Get Started Free
          </Link>
        </div>
      </Layout>
    );
  }

  const stats = [
    { label: 'Active Agents', value: '12', icon: Bot, color: 'text-blue-400' },
    { label: 'Total Projects', value: '4', icon: FolderKanban, color: 'text-indigo-400' },
    { label: 'Workflows', value: '8', icon: Workflow, color: 'text-purple-400' },
    { label: 'Requests/sec', value: '124', icon: Activity, color: 'text-emerald-400' },
  ];

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <header className="mb-10">
          <h2 className="text-3xl font-bold">Welcome back, {user.name.split(' ')[0]}!</h2>
          <p className="text-slate-400">Here's what's happening in <span className="text-blue-400 font-medium">{currentOrganization?.name}</span> today.</p>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {stats.map((stat, i) => (
            <div key={i} className="bg-slate-800 border border-slate-700 p-6 rounded-2xl shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-2 bg-slate-900 rounded-lg ${stat.color}`}>
                  <stat.icon size={24} />
                </div>
                <span className="text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded">+12%</span>
              </div>
              <p className="text-slate-400 text-sm font-medium">{stat.label}</p>
              <h3 className="text-3xl font-bold mt-1">{stat.value}</h3>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2 space-y-8">
            <section>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">Recent Projects</h3>
                <Link href="/projects" className="text-blue-400 text-sm hover:underline">View All</Link>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[1, 2].map(i => (
                  <div key={i} className="bg-slate-800 border border-slate-700 p-5 rounded-xl hover:border-slate-500 transition-colors cursor-pointer group">
                    <div className="flex items-center justify-between mb-3">
                      <div className="h-10 w-10 bg-indigo-900/30 rounded-lg flex items-center justify-center text-indigo-400">
                        <FolderKanban size={20} />
                      </div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Updated 2h ago</span>
                    </div>
                    <h4 className="font-bold mb-1 group-hover:text-blue-400 transition-colors">Project Alpha</h4>
                    <p className="text-sm text-slate-400 line-clamp-2">Infrastructure monitoring and auto-remediation agents.</p>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">Active Workflows</h3>
                <Link href="/workflow" className="text-blue-400 text-sm hover:underline">Editor</Link>
              </div>
              <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider">
                    <tr>
                      <th className="px-6 py-4 font-medium">Workflow</th>
                      <th className="px-6 py-4 font-medium">Status</th>
                      <th className="px-6 py-4 font-medium">Agents</th>
                      <th className="px-6 py-4 font-medium text-right">Activity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {[1, 2, 3].map(i => (
                      <tr key={i} className="hover:bg-slate-700/30 transition-colors">
                        <td className="px-6 py-4 font-medium text-sm">Customer Support Loop</td>
                        <td className="px-6 py-4">
                          <span className="flex items-center text-xs text-emerald-400">
                            <span className="h-1.5 w-1.5 bg-emerald-400 rounded-full mr-2 animate-pulse"></span>
                            Running
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-400">4 Agents</td>
                        <td className="px-6 py-4 text-right text-xs text-slate-500 font-mono">2,431 calls</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            <section className="bg-slate-800 border border-slate-700 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-4">Organization Team</h3>
              <div className="space-y-4">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="flex items-center space-x-3">
                    <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold border border-slate-600">
                      {['JD', 'AS', 'MK', 'PL'][i-1]}
                    </div>
                    <div className="flex-grow">
                      <p className="text-sm font-medium leading-none">Team Member {i}</p>
                      <p className="text-[10px] text-slate-500 mt-1">Software Engineer</p>
                    </div>
                    <div className={`h-2 w-2 rounded-full ${i % 3 === 0 ? 'bg-slate-600' : 'bg-emerald-500'}`}></div>
                  </div>
                ))}
              </div>
              <button className="w-full mt-6 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-xs font-medium transition-colors flex items-center justify-center">
                <Plus size={14} className="mr-2" />
                Invite Members
              </button>
            </section>

            <section className="bg-gradient-to-br from-indigo-900/40 to-blue-900/40 border border-blue-500/20 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-2">Build New Agent</h3>
              <p className="text-sm text-slate-300 mb-6">Create a specialized AI agent with custom tools and MCP integration.</p>
              <Link href="/agents" className="block w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-xl text-center text-sm font-bold transition-all shadow-lg shadow-blue-900/40">
                Launch Agent Builder
              </Link>
            </section>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;