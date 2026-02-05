/**
 * Next.js Configuration with Bundle Analyzer
 *
 * Usage: ANALYZE=true npm run build
 */

import type { NextConfig } from 'next'

const config: NextConfig = {
  // Your existing Next.js config
}

// Only enable bundle analyzer when ANALYZE=true
if (process.env.ANALYZE === 'true') {
  const withBundleAnalyzer = require('@next/bundle-analyzer')({
    enabled: true,
    openAnalyzer: true,
  })

  module.exports = withBundleAnalyzer(config)
} else {
  module.exports = config
}
