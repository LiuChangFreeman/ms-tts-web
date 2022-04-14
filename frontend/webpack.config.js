const path = require("path");
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
publicPath="./"

module.exports = {
  mode: "production",
  devServer: {
    contentBase:path.join(__dirname,"dist"),
    host:"0.0.0.0",
    port:80,
    disableHostCheck: true,
  },
  entry: {
    index:path.join(__dirname,"src", "index.js"),
  },
  output: {
    path: path.join(__dirname, "dist"),
    filename: "[name].[chunkhash].js",
    publicPath: publicPath
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              plugins: [
              ],
              compact:true
            },
          }
        ],
      },
      {
        test: /\.css$/,
        use: [
          'style-loader','css-loader'
        ],
      },
      {
        test: /\.svg$/,
        use: [
          'svg-loader'
        ],
      }
    ]
  },
  plugins: [
    new CleanWebpackPlugin(),
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname,'public','index.html'),
      publicPath:publicPath
    }),
    new CopyWebpackPlugin({
      patterns:[
        {
          from: __dirname+'/public/',
          to: __dirname+'/dist/'
        }
      ]
    })
  ],
  optimization: {
    runtimeChunk: {
      name: 'manifest',
    },
    splitChunks: {
      chunks: "all",
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendor",
          filename: "[name].[chunkhash].js",
          priority: -10
        },
        utilCommon: {
          name: "common",
          minSize: 0,
          minChunks: 2,
          priority: -20
        }
      }
    }
  },
};
