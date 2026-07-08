const path = require("path");

const webpackConfig = {
  eslint: {
    enable: false,
  },
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      webpackConfig.watchOptions = {
        ...webpackConfig.watchOptions,
        ignored: ['**/node_modules/**', '**/.git/**', '**/build/**'],
      };
      return webpackConfig;
    },
  },
};

module.exports = webpackConfig;
