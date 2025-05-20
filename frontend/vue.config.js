module.exports = {
  publicPath: process.env.BASE_URL || '/',
  outputDir: 'dist',
  assetsDir: 'static',
  devServer: {
    port: 8080,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    },
  },
  // Disable ESLint during development
  lintOnSave: false
};