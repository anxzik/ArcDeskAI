import React from 'react';
import Layout from '@/components/Layout';
import { FolderKanban, Plus, MoreVertical, Users } from 'lucide-react';
import useStore from '@/store';

const ProjectsPage = () => {
  const { currentOrganization } = useStore();

  const dummyProjects = [
    { id: 1, name: 'Customer Support Automation', description: 'Automating L1 support using agents.', team: 'Support Team', status: 'In Progress' },
    { id: 2, name: 'Market Analysis', description: 'Collecting and analyzing market trends.', team: 'Growth Team', status: 'Planning' },
  ];

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-2">Projects</h2>
            <p className="text-slate-400">Manage projects for {currentOrganization?.name || 'your organization'}.</p>
          </div>
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Plus size={18} />
            <span>New Project</span>
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {dummyProjects.map((project) => (
            <div key={project.id} className="bg-slate-800 border border-slate-700 rounded-xl p-5 hover:bg-slate-800/80 transition-colors flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-indigo-900/30 rounded-lg text-indigo-400">
                  <FolderKanban size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold">{project.name}</h3>
                  <p className="text-slate-400 text-sm">{project.description}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-8">
                <div className="flex items-center space-x-2 text-slate-400">
                  <Users size={16} />
                  <span className="text-sm">{project.team}</span>
                </div>
                <div className="px-3 py-1 bg-blue-900/30 text-blue-400 rounded-full text-xs font-medium border border-blue-500/30">
                  {project.status}
                </div>
                <button className="p-2 text-slate-500 hover:text-white transition-colors">
                  <MoreVertical size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default ProjectsPage;
