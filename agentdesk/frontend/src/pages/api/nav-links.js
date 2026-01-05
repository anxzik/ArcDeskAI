// pages/api/nav-links.js
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  // 1. Locate the 'pages' directory
  const pagesDir = path.join(process.cwd(), 'src', 'pages');

  // 2. Read the directory
  const fileNames = fs.readdirSync(pagesDir);

  // 3. Filter and Format
  const routes = fileNames
    .filter((file) => {
      // Ignore Next.js internal files, API folder, and hidden files
      return (
        !file.startsWith('_') && // _app.js, _document.js, _error.js
        !file.startsWith('.') && // .DS_Store
        file !== 'api' &&        // Ignore API routes
        file !== '404.js' &&     // Ignore error pages
        file !== '500.js'
      );
    })
    .map((file) => {
      // Remove extensions (.js, .tsx, etc)
      const name = file.replace(/\.(js|jsx|ts|tsx)$/, '');
      
      // Handle the root index page
      if (name === 'index') {
        return { label: 'Home', href: '/' };
      }

      // Format other pages (e.g., "about-us" -> "About Us")
      return {
        label: name
          .replace(/-/g, ' ')
          .replace(/\b\w/g, (c) => c.toUpperCase()),
        href: `/${name}`,
      };
    });

  // Optional: Sort Home to the top, others alphabetically
  routes.sort((a, b) => {
    if (a.href === '/') return -1;
    if (b.href === '/') return 1;
    return a.label.localeCompare(b.label);
  });

  res.status(200).json(routes);
}
