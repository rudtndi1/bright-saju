/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  // GitHub Pages 배포 시 basePath 설정 (필요시)
  // basePath: '/bright-saju',
  // assetPrefix: '/bright-saju/',
}

module.exports = nextConfig