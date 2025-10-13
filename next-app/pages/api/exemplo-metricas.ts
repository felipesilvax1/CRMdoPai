// ═══════════════════════════════════════════════════════════════
// API Route: Exemplo de Instrumentação com Métricas
// ═══════════════════════════════════════════════════════════════
// Demonstra como registrar métricas em uma API route
// Acesso: POST /api/exemplo-metricas
// ═══════════════════════════════════════════════════════════════

import type { NextApiRequest, NextApiResponse } from 'next';
import { 
  recordSearch, 
  recordDBQuery, 
  recordError,
  activeUsersGauge 
} from '../../lib/metrics';

type ExemploResponse = {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ExemploResponse>
) {
  const startTime = Date.now();

  try {
    // Simula uma consulta ao banco
    const dbStartTime = Date.now();
    
    // Simula delay de consulta
    await new Promise(resolve => setTimeout(resolve, Math.random() * 500));
    
    const dbDuration = (Date.now() - dbStartTime) / 1000;
    
    // Registra métricas da consulta ao banco
    recordDBQuery('select_empresas', 'success', dbDuration);
    
    // Registra a busca realizada
    recordSearch('filtros', 'success');
    
    // Simula incremento de usuários ativos (geralmente feito via middleware)
    activeUsersGauge.inc();

    // Retorna resultado simulado
    res.status(200).json({
      success: true,
      message: 'Consulta executada com sucesso',
      data: {
        resultados: 150,
        tempo_consulta: dbDuration.toFixed(3) + 's',
      },
    });

  } catch (error) {
    // Registra o erro
    recordError('query_error', '/api/exemplo-metricas');
    recordSearch('filtros', 'error');

    console.error('Erro na consulta:', error);
    res.status(500).json({
      success: false,
      message: 'Erro ao executar consulta',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  } finally {
    // Sempre decrementa usuários ativos
    activeUsersGauge.dec();
  }
}

