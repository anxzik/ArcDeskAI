import React from 'react';
import NavBar from './NavBar'

const Layout = ({ children }) => {
  return (
    <div className="bg-slate-900 text-white min-h-screen">
      <NavBar/>
      <main className="p-4">
        {children}
      </main>
    </div>
  );
};

export default Layout;
