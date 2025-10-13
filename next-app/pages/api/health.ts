// ═══════════════════════════════════════════════════════════════
// API Route: Health Check
// ═══════════════════════════════════════════════════════════════
// Endpoint para verificação de saúde da aplicação
// Acesso: GET /api/health
// ═══════════════════════════════════════════════════════════════

import type { NextApiRequest, NextApiResponse } from 'next';

type HealthResponse = {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  uptime: number;
  environment: string;
  version: string;
  services?: {
    api?: string;
    llm?: string;
    database?: string;
  };
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthResponse>
) {
  // Apenas aceita método GET
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).end();
  }

  try {
    // Informações básicas de saúde
    const healthData: HealthResponse = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '0.1.0',
    };

    // Retorna 200 se saudável
    res.status(200).json(healthData);
  } catch (error) {
    // Retorna 503 se não saudável
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '0.1.0',
    });
  }
}

