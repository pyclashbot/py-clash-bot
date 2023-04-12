/** @type {import('next').NextConfig} */

module.exports = {
  images: {
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
