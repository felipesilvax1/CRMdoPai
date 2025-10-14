// Proxy simples para redirecionar 192.168.15.22:5000 → localhost:5000 (Docker)
const http = require('http');
const httpProxy = require('http-proxy');

const proxy = httpProxy.createProxyServer({});

const server = http.createServer((req, res) => {
  // Adicionar CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  console.log(`→ ${req.method} ${req.url}`);
  
  // Redirecionar para Docker (localhost:5000)
  proxy.web(req, res, {
    target: 'http://localhost:5000',
    changeOrigin: true
  });
});

// Escutar em TODAS as interfaces na porta 5001
server.listen(5001, '0.0.0.0', () => {
  console.log('🚀 Proxy rodando em http://0.0.0.0:5001');
  console.log('📡 Redirecionando para http://localhost:5000 (Docker)');
  console.log('🌐 Acessível de qualquer dispositivo via http://192.168.15.22:5001');
});

proxy.on('error', (err, req, res) => {
  console.error('❌ Erro no proxy:', err.message);
  res.writeHead(500, { 'Content-Type': 'text/plain' });
  res.end('Proxy error: ' + err.message);
});



