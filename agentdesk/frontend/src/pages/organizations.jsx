import React from 'react';
import Layout from '@/components/Layout';
import useStore from '@/store';
import { Building2, Plus, Settings, Users } from 'lucide-react';

const OrganizationsPage = () => {
  const { organizations, currentOrganization, setCurrentOrganization } = useStore();

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold">Organizations</h2>
            <p className="text-slate-400">Manage your workspace and teams.</p>
          </div>
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Plus size={18} />
            <span>Create Organization</span>
          </button>
        </div>

        <div className="space-y-4">
          {organizations.map((org) => (
            <div 
              key={org.id} 
              className={`bg-slate-800 border ${currentOrganization?.id === org.id ? 'border-blue-500' : 'border-slate-700'} rounded-xl p-6 flex items-center justify-between`}
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-slate-700 rounded-lg text-blue-400">
                  <Building2 size={24} />
                </div>
                <div>
                  <h3 className="text-xl font-bold">{org.name}</h3>
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="flex items-center text-sm text-slate-400">
                      <Users size={14} className="mr-1" />
                      12 Members
                    </span>
                    <span className="flex items-center text-sm text-slate-400">
                      <Settings size={14} className="mr-1" />
                      Admin Role
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                {currentOrganization?.id === org.id ? (
                  <span className="px-3 py-1 bg-blue-900/30 text-blue-400 rounded-full text-xs font-medium border border-blue-500/30">
                    Active
                  </span>
                ) : (
                  <button 
                    onClick={() => setCurrentOrganization(org)}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium transition-colors"
                  >
                    Switch to
                  </button>
                )}
                <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-all">
                  <Settings size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default OrganizationsPage;
