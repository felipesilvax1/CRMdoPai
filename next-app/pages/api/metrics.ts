// ═══════════════════════════════════════════════════════════════
// API Route: Métricas do Prometheus
// ═══════════════════════════════════════════════════════════════
// Endpoint que expõe métricas no formato do Prometheus
// Acesso: GET /api/metrics
// ═══════════════════════════════════════════════════════════════

import type { NextApiRequest, NextApiResponse } from 'next';
import { metricsRegistry } from '../../lib/metrics';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Apenas aceita método GET
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: `Method ${req.method} Not Allowed` });
  }

  try {
    // Define o content-type apropriado para o Prometheus
    res.setHeader('Content-Type', metricsRegistry.contentType);
    
    // Retorna as métricas no formato texto do Prometheus
    const metrics = await metricsRegistry.metrics();
    res.status(200).send(metrics);
  } catch (error) {
    console.error('Erro ao gerar métricas:', error);
    res.status(500).json({ 
      error: 'Erro ao gerar métricas',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

