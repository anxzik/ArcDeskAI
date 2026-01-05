/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/agents/:path*',
        destination: 'http://localhost:8001/agents/:path*',
      },
      {
        source: '/knowledge-bases/:path*',
        destination: 'http://localhost:8001/knowledge-bases/:path*',
      },
      {
        source: '/datasources/:path*',
        destination: 'http://localhost:8001/datasources/:path*',
      },
      {
        source: '/mcp/:path*',
        destination: 'http://localhost:8001/mcp/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
