import React from 'react';

const Layout = ({ children }) => {
  return (
    <div className="bg-slate-900 text-white min-h-screen">
      <nav className="bg-slate-800 p-4">
        <h1 className="text-2xl">ArcDeskAI</h1>
      </nav>
      <main className="p-4">
        {children}
      </main>
    </div>
  );
};

export default Layout;
