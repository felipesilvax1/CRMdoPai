// API Proxy - Redireciona /api/proxy/* para http://192.168.15.22:5000/*
export default async function handler(req, res) {
  const { path } = req.query;
  const apiPath = Array.isArray(path) ? path.join('/') : path;
  
  // API rodando no container Docker
  const API_URL = 'http://192.168.15.22:5000';
  const targetUrl = `${API_URL}/${apiPath}${req.url.includes('?') ? '?' + req.url.split('?')[1] : ''}`;
  
  console.log(`[PROXY] ${req.method} /api/proxy/${apiPath} → ${targetUrl}`);
  
  try {
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined,
    });
    
    const contentType = response.headers.get('content-type');
    
    // Verificar se é JSON
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      res.status(response.status).json(data);
    } else {
      // Se não for JSON (ex: HTML de erro 404), retornar como texto
      const text = await response.text();
      console.log(`[PROXY] Resposta não-JSON (${response.status}):`, text.substring(0, 100));
      res.status(response.status).json({ 
        erro: `Endpoint não encontrado: /${apiPath}`,
        status: response.status 
      });
    }
  } catch (error) {
    console.error('[PROXY] Erro:', error.message);
    res.status(500).json({ erro: `Proxy error: ${error.message}` });
  }
}

