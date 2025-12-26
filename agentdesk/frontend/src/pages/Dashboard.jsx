import React, { useEffect, useState } from 'react';
import { getAgents, getTasks } from '../services/api';
import { Users, CheckSquare, Activity, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const StatCard = ({ title, value, icon, color, to }) => {
  const Icon = icon;
  return (
  <Link to={to} className="block group">
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 transition-all group-hover:border-slate-700 group-hover:shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-opacity-10 ${color}`}>
          <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
        </div>
        <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300" />
      </div>
      <h3 className="text-slate-400 text-sm font-medium">{title}</h3>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
  </Link>
);
};

const Dashboard = () => {
  const [stats, setStats] = useState({ agents: 0, tasks: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [agentsData, tasksData] = await Promise.all([
          getAgents(),
          getTasks()
        ]);
        setStats({
          agents: agentsData.length,
          tasks: tasksData.length
        });
      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="text-slate-400">Loading stats...</div>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold text-white mb-8">Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard 
          title="Active Agents" 
          value={stats.agents} 
          icon={Users} 
          color="bg-blue-500 text-blue-500"
          to="/agents"
        />
        <StatCard 
          title="Total Tasks" 
          value={stats.tasks} 
          icon={CheckSquare} 
          color="bg-emerald-500 text-emerald-500"
          to="/tasks"
        />
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-purple-500/10 text-purple-500">
              <Activity className="w-6 h-6" />
            </div>
          </div>
          <h3 className="text-slate-400 text-sm font-medium">System Status</h3>
          <p className="text-2xl font-bold text-white mt-1">Operational</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
