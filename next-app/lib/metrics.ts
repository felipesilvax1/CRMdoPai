// ═══════════════════════════════════════════════════════════════
// Módulo de Métricas do Prometheus
// ═══════════════════════════════════════════════════════════════
// Exporta métricas personalizadas para monitoramento da aplicação
// ═══════════════════════════════════════════════════════════════

import { register, Counter, Histogram, Gauge } from 'prom-client';

// ═══════════════════════════════════════════════════════════════
// Configuração do Registry
// ═══════════════════════════════════════════════════════════════

// Registry padrão (contém métricas default do Node.js)
export const metricsRegistry = register;

// Helper para obter ou criar métrica (evita duplicação)
function getOrCreateCounter(config: any) {
  try {
    return metricsRegistry.getSingleMetric(config.name) as Counter || new Counter(config);
  } catch {
    return new Counter(config);
  }
}

function getOrCreateHistogram(config: any) {
  try {
    return metricsRegistry.getSingleMetric(config.name) as Histogram || new Histogram(config);
  } catch {
    return new Histogram(config);
  }
}

function getOrCreateGauge(config: any) {
  try {
    return metricsRegistry.getSingleMetric(config.name) as Gauge || new Gauge(config);
  } catch {
    return new Gauge(config);
  }
}

// ═══════════════════════════════════════════════════════════════
// Métricas Personalizadas
// ═══════════════════════════════════════════════════════════════

/**
 * Contador de Buscas/Pesquisas
 * Incrementa cada vez que uma busca é realizada
 */
export const searchesCounter = getOrCreateCounter({
  name: 'crm_searches_total',
  help: 'Total de buscas realizadas no sistema',
  labelNames: ['search_type', 'status'],
  registers: [metricsRegistry],
});

/**
 * Histograma de Duração de Consultas LLM
 * Mede o tempo de resposta das consultas ao LLM
 */
export const llmDurationHistogram = getOrCreateHistogram({
  name: 'crm_llm_query_duration_seconds',
  help: 'Duração das consultas ao LLM em segundos',
  labelNames: ['model', 'status'],
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30], // Buckets em segundos
  registers: [metricsRegistry],
});

/**
 * Histograma de Duração de Consultas ao Banco de Dados
 * Mede o tempo de resposta das consultas ao PostgreSQL
 */
export const dbQueryDurationHistogram = getOrCreateHistogram({
  name: 'crm_db_query_duration_seconds',
  help: 'Duração das consultas ao banco de dados em segundos',
  labelNames: ['query_type', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5], // Buckets em segundos
  registers: [metricsRegistry],
});

/**
 * Contador de Erros
 * Incrementa cada vez que ocorre um erro na aplicação
 */
export const errorsCounter = getOrCreateCounter({
  name: 'crm_errors_total',
  help: 'Total de erros na aplicação',
  labelNames: ['error_type', 'page'],
  registers: [metricsRegistry],
});

/**
 * Gauge de Usuários Ativos
 * Rastreia o número de usuários ativos no momento
 */
export const activeUsersGauge = getOrCreateGauge({
  name: 'crm_active_users',
  help: 'Número de usuários ativos no sistema',
  registers: [metricsRegistry],
});

/**
 * Contador de Requisições HTTP
 * Incrementa para cada requisição HTTP recebida
 */
export const httpRequestsCounter = getOrCreateCounter({
  name: 'crm_http_requests_total',
  help: 'Total de requisições HTTP',
  labelNames: ['method', 'path', 'status'],
  registers: [metricsRegistry],
});

/**
 * Histograma de Duração de Requisições HTTP
 * Mede o tempo de resposta das requisições HTTP
 */
export const httpRequestDurationHistogram = getOrCreateHistogram({
  name: 'crm_http_request_duration_seconds',
  help: 'Duração das requisições HTTP em segundos',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
  registers: [metricsRegistry],
});

/**
 * Contador de Relatórios Gerados
 * Incrementa cada vez que um relatório é gerado
 */
export const reportsCounter = getOrCreateCounter({
  name: 'crm_reports_generated_total',
  help: 'Total de relatórios gerados',
  labelNames: ['format', 'status'],
  registers: [metricsRegistry],
});

/**
 * Gauge de Tamanho do Cache
 * Rastreia o número de items em cache
 */
export const cacheSizeGauge = getOrCreateGauge({
  name: 'crm_cache_size_items',
  help: 'Número de items no cache',
  labelNames: ['cache_type'],
  registers: [metricsRegistry],
});

// ═══════════════════════════════════════════════════════════════
// Funções Auxiliares
// ═══════════════════════════════════════════════════════════════

/**
 * Registra uma busca no sistema
 */
export function recordSearch(searchType: string, status: 'success' | 'error') {
  searchesCounter.inc({ search_type: searchType, status });
}

/**
 * Registra o tempo de uma consulta LLM
 */
export function recordLLMQuery(model: string, status: string, durationSeconds: number) {
  llmDurationHistogram.observe({ model, status }, durationSeconds);
}

/**
 * Registra o tempo de uma consulta ao banco
 */
export function recordDBQuery(queryType: string, status: string, durationSeconds: number) {
  dbQueryDurationHistogram.observe({ query_type: queryType, status }, durationSeconds);
}

/**
 * Registra um erro
 */
export function recordError(errorType: string, page: string) {
  errorsCounter.inc({ error_type: errorType, page });
}

/**
 * Registra uma requisição HTTP
 */
export function recordHTTPRequest(method: string, path: string, status: number, durationSeconds: number) {
  httpRequestsCounter.inc({ method, path, status: status.toString() });
  httpRequestDurationHistogram.observe({ method, path, status: status.toString() }, durationSeconds);
}

/**
 * Registra geração de relatório
 */
export function recordReport(format: string, status: 'success' | 'error') {
  reportsCounter.inc({ format, status });
}

