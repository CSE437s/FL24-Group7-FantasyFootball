/** @type {import('next').NextConfig} */
const nextConfig = {
    env: {
        YAHOO_CLIENT_ID: process.env.YAHOO_CLIENT_ID,
        YAHOO_CLIENT_SECRET: process.env.YAHOO_CLIENT_SECRET,
      },
};

export default nextConfig;
