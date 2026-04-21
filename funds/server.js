const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = 8080;

app.use(express.static(path.join(__dirname, 'web')));

app.use('/api/fundsuggest', createProxyMiddleware({
    target: 'https://fundsuggest.eastmoney.com',
    changeOrigin: true,
    pathRewrite: {
        '^/api/fundsuggest': ''
    },
    logLevel: 'info'
}));

app.use('/api/push2', createProxyMiddleware({
    target: 'https://push2.eastmoney.com',
    changeOrigin: true,
    pathRewrite: {
        '^/api/push2': ''
    },
    logLevel: 'info'
}));

app.use('/api/fundmobapi', createProxyMiddleware({
    target: 'https://fundmobapi.eastmoney.com',
    changeOrigin: true,
    pathRewrite: {
        '^/api/fundmobapi': ''
    },
    logLevel: 'info'
}));

app.listen(PORT, () => {
    console.log('========================================');
    console.log('  自选基金助手 Web版 代理服务器');
    console.log('========================================');
    console.log(`  服务器地址: http://localhost:${PORT}`);
    console.log(`  代理配置:`);
    console.log(`    /api/fundsuggest  -> https://fundsuggest.eastmoney.com`);
    console.log(`    /api/push2        -> https://push2.eastmoney.com`);
    console.log(`    /api/fundmobapi   -> https://fundmobapi.eastmoney.com`);
    console.log('========================================');
    console.log('  按 Ctrl+C 停止服务器');
    console.log('========================================');
});
