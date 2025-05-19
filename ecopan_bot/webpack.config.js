const path = require('path');
module.exports = {
  entry: './public/js/App.jsx',          // tuo punto di ingresso React
  output: {
    path: path.resolve(__dirname, 'public/js'),
    filename: 'chatbot.js'               // bundle che verrà symlinkato
  },
  module: {
    rules: [{
      test: /\.(js|jsx)$/,
      exclude: /node_modules/,
      use: {
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-env','@babel/preset-react']
        }
      }
    }]
  },
  resolve: { extensions: ['.js','.jsx'] },
  mode: 'production'
};