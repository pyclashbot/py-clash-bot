/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === "production";

module.exports = {
  assetPrefix: isProd ? "/py-clash-bot" : undefined,
  images: {
    unoptimized: true,
    dangerouslyAllowSVG: true,
    remotePatterns: [
      {
        protocol: "https",
        hostname: "www.codefactor.io",
      },
      {
        protocol: "https",
        hostname: "github.com",
      },
    ],
  },
};
