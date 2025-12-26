import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, CheckSquare, PlusCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const NavItem = ({ to, icon: Icon, children }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={twMerge(
        clsx(
          'flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-sm font-medium',
          isActive
            ? 'bg-blue-600 text-white'
            : 'text-slate-300 hover:bg-slate-800 hover:text-white'
        )
      )}
    >
      <Icon size={18} />
      {children}
    </Link>
  );
};

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            AgentDesk
          </h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          <NavItem to="/" icon={LayoutDashboard}>Dashboard</NavItem>
          <NavItem to="/agents" icon={Users}>Agents</NavItem>
          <NavItem to="/tasks" icon={CheckSquare}>Tasks</NavItem>
        </nav>

        <div className="p-4 border-t border-slate-800">
           <div className="text-xs text-slate-500">
             v0.1.0 Alpha
           </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
