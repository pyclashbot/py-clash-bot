/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === "production";

module.exports = {
  assetPrefix: isProd ? '/py-clash-bot' : '',
  images: {
    unoptimized: true,
  },
};
