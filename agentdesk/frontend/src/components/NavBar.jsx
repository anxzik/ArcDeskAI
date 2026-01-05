import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import useStore from '@/store';
import { LogOut, User, Building2, ChevronDown } from 'lucide-react';

const NavBar = () => {
  const router = useRouter();
  const { user, organizations, currentOrganization, setCurrentOrganization, logout } = useStore();
  const [links, setLinks] = useState([]);

  useEffect(() => {
    fetch('/api/nav-links')
      .then((res) => res.json())
      .then((data) => setLinks(data))
      .catch((err) => console.error('Failed to load menu:', err));
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  return (
    <nav className="bg-slate-800 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                ArcDeskAI
              </span>
            </Link>
            
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {links.map((link) => {
                const isActive = router.pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`${
                      isActive 
                        ? 'border-blue-500 text-white' 
                        : 'border-transparent text-slate-300 hover:text-white hover:border-slate-300'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                {/* Org Selector */}
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-slate-300 hover:text-white text-sm font-medium">
                    <Building2 size={18} />
                    <span>{currentOrganization?.name || 'Select Org'}</span>
                    <ChevronDown size={14} />
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-slate-800 border border-slate-700 rounded-md shadow-lg py-1 hidden group-hover:block z-50">
                    {organizations.map((org) => (
                      <button
                        key={org.id}
                        onClick={() => setCurrentOrganization(org)}
                        className="block w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white"
                      >
                        {org.name}
                      </button>
                    ))}
                    <Link href="/organizations" className="block px-4 py-2 text-sm text-blue-400 hover:bg-slate-700">
                      Manage Orgs
                    </Link>
                  </div>
                </div>

                {/* User Menu */}
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-slate-300 hover:text-white">
                    <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center">
                      <User size={20} />
                    </div>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-slate-800 border border-slate-700 rounded-md shadow-lg py-1 hidden group-hover:block z-50">
                    <div className="px-4 py-2 text-xs text-slate-500 border-b border-slate-700">
                      Signed in as <br />
                      <span className="text-slate-300 font-medium">{user.email}</span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center px-4 py-2 text-sm text-red-400 hover:bg-slate-700"
                    >
                      <LogOut size={16} className="mr-2" />
                      Logout
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <Link
                href="/auth/login"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;