module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://backend:8002',
        changeOrigin: true
      }
    }
  }
} 