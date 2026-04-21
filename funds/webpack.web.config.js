const webpack = require('webpack');
const ejs = require('ejs');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyPlugin = require('copy-webpack-plugin');
const {
  VueLoaderPlugin
} = require('vue-loader');
const {
  version
} = require('./package.json');
const path = require('path');

const config = {
  mode: process.env.NODE_ENV,
  context: __dirname + '/src',
  entry: {
    'main': './web/main.js',
  },
  output: {
    path: __dirname + '/dist-web',
    filename: '[name].js',
  },
  resolve: {
    extensions: ['.js', '.vue'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'common': path.resolve(__dirname, 'src/common'),
    }
  },
  module: {
    rules: [{
        test: /\.vue$/,
        loaders: 'vue-loader',
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader'],
      },
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader'],
      },
      {
        test: /\.sass$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader?indentedSyntax'],
      },
      {
        test: /\.(png|jpg|jpeg|gif|svg|ico)$/,
        loader: 'file-loader',
        options: {
          name: '[path][name].[ext]',
          outputPath: '/images/',
          emitFile: true,
          esModule: false,
        },
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'file-loader',
        options: {
          name: '[path][name].[ext]',
          outputPath: '/fonts/',
          emitFile: true,
          esModule: false,
        },
      },
    ],
  },
  plugins: [
    new webpack.DefinePlugin({
      global: 'window',
    }),
    new VueLoaderPlugin(),
    new MiniCssExtractPlugin({
      filename: '[name].css',
    }),
    new CopyPlugin([{
        from: 'icons',
        to: 'icons',
        ignore: ['icon.xcf']
      },
      {
        from: 'web/index.html',
        to: 'index.html',
        transform: transformHtml
      },
    ]),
  ],
  devServer: {
    contentBase: path.join(__dirname, 'dist-web'),
    compress: true,
    port: 8080,
    hot: true,
    proxy: {
      '/api/fundsuggest': {
        target: 'https://fundsuggest.eastmoney.com',
        changeOrigin: true,
        pathRewrite: {
          '^/api/fundsuggest': ''
        }
      },
      '/api/push2': {
        target: 'https://push2.eastmoney.com',
        changeOrigin: true,
        pathRewrite: {
          '^/api/push2': ''
        }
      },
      '/api/fundmobapi': {
        target: 'https://fundmobapi.eastmoney.com',
        changeOrigin: true,
        pathRewrite: {
          '^/api/fundmobapi': ''
        }
      }
    }
  }
};

if (config.mode === 'production') {
  config.plugins = (config.plugins || []).concat([
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: '"production"',
      },
    }),
  ]);
}

function transformHtml(content) {
  return ejs.render(content.toString(), {
    ...process.env,
    version: version,
  });
}

module.exports = config;
